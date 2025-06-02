import os
import urllib
import click
from flask import Flask, jsonify, request, redirect, url_for
from db import db
from Models.Product import Product
from Models.Order import Order
from Models.Shipping_information import Shipping_information
from Models.Transaction import Transaction
from Models.CreditCard import CreditCard
from services import fetch_and_store_products
from ErrorMessage import *
import json
import logging
from logging.handlers import RotatingFileHandler
import time

app = Flask(__name__)

os.makedirs("../logs", exist_ok=True)
log_path = os.path.join("../logs", "api.log")
handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([Product, Order, Shipping_information, Transaction, CreditCard])
    fetch_and_store_products()
    click.echo("Base de données initialisée avec succès.")

@app.before_request
def log_request_info():
    request.start_time = time.time()
    logger.info(f"Requête entrante: {request.method} {request.path} - IP: {request.remote_addr}")
    if request.method in ["POST", "PUT"]:
        logger.debug(f"Payload: {request.get_json(silent=True)}")

@app.after_request
def log_response_info(response):
    duration = round((time.time() - request.start_time) * 1000, 2)
    logger.info(f"Réponse {request.method} {request.path} - {response.status_code} en {duration}ms")
    return response

@app.route("/", methods=["GET"])
def get_products():
    products = Product.select()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "image": p.image,
            "weight": p.weight,
            "price": p.price,
            "in_stock": p.in_stock
        })
    return jsonify({"products": result}), 200

@app.route("/order", methods=["POST"])
def create_order():
    data = request.get_json()

    # Vérification de l'objet "product"
    if not data or "product" not in data:
        return Error422OrderNeedProduct

    product_data = data["product"]
    if "id" not in product_data or "quantity" not in product_data:
        return Error422OrderNeedProduct

    product_id = product_data["id"]
    quantity = product_data["quantity"]

    if quantity < 1:
        return Error422OrderNeedProduct

    try:
        product = Product.get(Product.id == product_id)
    except Product.DoesNotExist:
        return Error422OrderDoesNotExist

    if not product.in_stock:
        return Error422ProductOutOfInventory

    order = Order.create(product=product, quantity=quantity, shipping_price=product.price)
    return redirect(f"/order/{order.id}", code=302)

@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return {"error": "Commande non trouvée"}, 404

    return order.load_object_to_json() , 200

@app.route("/order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json()

    # Trouver la commande
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return {"error": "Commande non trouvée"}, 404

    # cas ajout information client
    if "order" in data:
        order_data = data.get("order", {})

        email = order_data.get("email")
        shipping_info = order_data.get("shipping_information", {})

        required_fields = ["country", "address", "postal_code", "city", "province"]
        missing_fields = [
            f for f in required_fields if not shipping_info.get(f)
        ]

        if not email and (not shipping_info or missing_fields):
            return Error422OneOrMoreMissingField

        if shipping_info and missing_fields:
            return Error422OneOrMoreMissingField

        if email:
            if order.is_valid_email(email):
                order.email = email
            else:
                return Error422InvalidEmailformat

        if shipping_info:
            new_shipping_information = Shipping_information.from_dict(shipping_info)
            new_shipping_information.save()
            order.shipping_information = new_shipping_information

            # Calcul du prix
            product = order.product
            quantity = order.quantity
            total_price = int(product.price * quantity)
            order.total_price = total_price

            # Calcul des frais de port
            weight = product.weight * quantity
            if weight <= 500:
                shipping_price = 500
            elif weight <= 2000:
                shipping_price = 1000
            else:
                shipping_price = 2500
            order.shipping_price = shipping_price

            # Taxe selon province
            province = new_shipping_information.province
            if order.is_valid_province(province):
                taxes = {
                    "QC": 0.15,
                    "ON": 0.13,
                    "AB": 0.05,
                    "BC": 0.12,
                    "NS": 0.14
                }
                tax_rate = taxes.get(province.upper(), 0)
                order.total_price_tax = round(total_price * (1 + tax_rate), 2)
            else:
                return Error422Invalidprovincevalue
        order.save()

    #cas paiment par carte
    elif "credit_card" in data:
        if "order" in data:
            return Error422CanNotGiveCardAndShippingInfoOrEmail

        if order.paid:
            return Error422OrderAlreadyBuy

        if not order.email or not order.shipping_information:
            return Error422NeedShippingInfoBeforCreditCard

        credit_card = data["credit_card"]
        amount_charged = order.total_price + order.shipping_price

        # Appel au service de paiement distant
        payment_payload = json.dumps({
            "credit_card": credit_card,
            "amount_charged": amount_charged
        }).encode("utf-8")

        req = urllib.request.Request(
            url="https://dimensweb.uqac.ca/~jgnault/shops/pay/",
            data=payment_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                payment_response = json.loads(response.read().decode())
                order.paid = True
                new_credit_card = CreditCard.from_dict(payment_response["credit_card"])
                new_credit_card.save()
                order.credit_card = new_credit_card
                new_transaction = Transaction.from_dict(payment_response["transaction"])
                new_transaction.save()
                order.transaction = new_transaction
                order.save()
        except urllib.error.HTTPError as e:
            error_response = json.loads(e.read().decode())
            return error_response, 422
    else:
        return Error422NonCompliantFields

    return order.load_object_to_json(), 200

app.run(debug=True)