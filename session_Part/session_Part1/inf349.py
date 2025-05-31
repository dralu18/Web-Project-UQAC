import click
from flask import Flask, jsonify, request, redirect, url_for
from db import db
from Models.Product import Product
from Models.Order import Order
from services import fetch_and_store_products
from ErrorMessage import *
import json

from session_Part.Models.Shipping_information import Shipping_information

app = Flask(__name__)

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([Product, Order])
    fetch_and_store_products()
    click.echo("Base de données initialisée avec succès.")

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

    order = Order.create(product=product, quantity=quantity)
    return redirect(f"/order/{order.id}", code=302)

@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return {"error": "Commande non trouvée"}, 404

    return {
        "order": {
            "id": order.id,
            "total_price": order.total_price,
            "total_price_tax": order.total_price_tax,
            "email": order.email,
            "credit_card": json.loads(order.credit_card) if order.credit_card else {},
            "shipping_information": json.loads(order.shipping_information) if order.shipping_information else {},
            "transaction": json.loads(order.transaction) if order.transaction else {},
            "paid": order.paid,
            "product": {
            "id": order.product.id,
            "quantity": order.quantity
        },
        "shipping_price": order.shipping_price
    }
}, 200

@app.route("/order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json()

    # Trouver la commande
    try:
        order = Order.get_by_id(order_id)
    except Order.DoesNotExist:
        return {"error": "Commande non trouvée"}, 404

    order_data = data.get("order", {})

    email = order_data.get("email")
    shipping_info = order_data.get("shipping_information", {})

    required_fields = ["country", "address", "postal_code", "city", "province"]
    missing_fields = [
        f for f in required_fields if f not in shipping_info or not shipping_info[f]
    ]

    if not email or not shipping_info or missing_fields:
        return {
            "errors": {
                "order": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires"
                }
            }
        }, 422

    # Stocker shipping_information comme JSON string
    order.email = email
    shipping_information = Shipping_information(json.dumps(shipping_info))
    shipping_information.save()
    order.shipping_information = shipping_information.id

    # Calcul prix total + taxes + expédition
    product = order.product
    quantity = order.quantity
    total_price = int(product.price * quantity)
    order.total_price = total_price

    # Calcul frais d'expédition
    weight = product.weight * quantity
    if weight <= 500:
        shipping_price = 500
    elif weight <= 2000:
        shipping_price = 1000
    else:
        shipping_price = 2500
    order.shipping_price = shipping_price

    # Taxe selon province
    province = shipping_info["province"]
    taxes = {
        "QC": 0.15,
        "ON": 0.13,
        "AB": 0.05,
        "BC": 0.12,
        "NS": 0.14
    }
    tax_rate = taxes.get(province.upper(), 0)
    order.total_price_tax = round(total_price * (1 + tax_rate), 2)

    order.save()

    return {
        "order": {
            "id": order.id,
            "email": order.email,
            "shipping_information": json.loads(order.shipping_information),
            "credit_card": json.loads(order.credit_card) if order.credit_card else {},
            "transaction": json.loads(order.transaction) if order.transaction else {},
            "paid": order.paid,
            "product": {
                "id": product.id,
                "quantity": order.quantity
            },
            "shipping_price": order.shipping_price,
            "total_price": order.total_price,
            "total_price_tax": order.total_price_tax
        }
    }, 200

app.run(debug=True)