import os
import urllib
import click
import json
import logging
import time
from flask import Flask, jsonify, request, redirect
from session_Part.db import db
from session_Part.Models.Product import Product
from session_Part.Models.Order import Order
from session_Part.Models.Shipping_information import Shipping_information
from session_Part.Models.Transaction import Transaction
from session_Part.Models.CreditCard import CreditCard
from session_Part.services import fetch_and_store_products
from session_Part.ErrorMessage import *
from logging.handlers import RotatingFileHandler

global app

app = Flask(__name__)

app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), 'Bat_File', 'shop.db')


db.init(app.config["DATABASE"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

log_path = os.path.join(logs_dir, "api.log")
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

    if not data or "product" not in data:
        logger.warning("Données manquantes ou clé 'product' absente dans le payload.")
        return Error422OrderNeedProduct

    product_data = data["product"]
    if "id" not in product_data or "quantity" not in product_data:
        logger.warning("Clés 'id' ou 'quantity' manquantes dans 'product'.")
        return Error422OrderNeedProduct

    product_id = product_data["id"]
    quantity = product_data["quantity"]

    if quantity < 1:
        logger.warning(f"Quantité invalide ({quantity}) pour le produit {product_id}.")
        return Error422OrderNeedProduct

    try:
        product = Product.get(Product.id == product_id)
    except Product.DoesNotExist:
        logger.warning(f"Produit avec ID {product_id} non trouvé.")
        return Error422OrderDoesNotExist

    if not product.in_stock:
        logger.info(f"Produit {product.name} (ID {product.id}) hors stock.")
        return Error422ProductOutOfInventory

    order = Order.create(product=product, quantity=quantity, total_price=product.price * quantity, shipping_price=product.calculate_weight(quantity))
    logger.info(f"Commande {order.id} créée avec succès pour le produit {product.name} (ID {product.id}), quantité {quantity}.")
    return redirect(f"/order/{order.id}", code=302)

@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        logger.warning(f"Commande {order_id} non trouvée.")
        return {"error": "Commande non trouvée"}, 404

    logger.info(f"Commande {order_id} récupérée avec succès.")
    return order.load_object_to_json() , 200

@app.route("/order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json()
    if not data:
        logger.warning(f"Aucun JSON reçu pour la commande {order_id}")
        return Error422NonCompliantFields

    # Trouver la commande
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        logger.warning(f"Commande {order_id} non trouvée.")
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
            logger.warning(f"Champs requis manquants pour la commande {order_id}: {missing_fields}")
            return Error422OneOrMoreMissingField

        if shipping_info and missing_fields:
            logger.warning(f"Infos de livraison incomplètes pour la commande {order_id}: {missing_fields}")
            return Error422OneOrMoreMissingField

        if email:
            if order.is_valid_email(email):
                logger.info(f"Email mis à jour pour la commande {order_id}: {email}")
                order.email = email
            else:
                logger.warning(f"Format d'email invalide pour la commande {order_id}: {email}")
                return Error422InvalidEmailformat

        if shipping_info:
            logger.info(f"Infos de livraison ajoutées pour la commande {order_id}")
            new_shipping_information = Shipping_information.from_dict(shipping_info)
            new_shipping_information.save()
            order.shipping_information = new_shipping_information

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
                order.total_price_tax = round(order.total_price * (1 + tax_rate), 2)
                logger.info(f"Taxe appliquée pour {province} sur la commande {order_id}: {tax_rate * 100}%")
            else:
                logger.warning(f"Province invalide '{province}' pour la commande {order_id}")
                return Error422Invalidprovincevalue
        order.save()
        logger.info(f"Infos client enregistrées avec succès pour la commande {order_id}")

    #cas paiment par carte
    elif "credit_card" in data:
        logger.info(f"Paiement par carte pour la commande {order_id}")
        if "order" in data:
            logger.warning(f"Conflit : données carte + infos client fournies pour la commande {order_id}")
            return Error422CanNotGiveCardAndShippingInfoOrEmail

        if order.paid:
            logger.warning(f"Commande {order_id} déjà payée.")
            return Error422OrderAlreadyBuy

        if not order.email or not order.shipping_information:
            logger.warning(f"Impossible de payer la commande {order_id} sans email et infos livraison.")
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
                logger.info(f"Paiement réussi pour la commande {order_id} - {amount_charged} cents")
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
            logger.error(f"Échec du paiement pour la commande {order_id}: {error_response}")
            return error_response, 422
    else:
        logger.warning(f"Champs invalides ou manquants dans la requête PUT pour la commande {order_id}")
        return Error422NonCompliantFields

    logger.info(f"Mise à jour terminée pour la commande {order_id}")
    return order.load_object_to_json(), 200

if __name__ == "__main__":
    app.run(debug=True)