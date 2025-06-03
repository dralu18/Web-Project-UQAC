import json
import pytest
from peewee import SqliteDatabase
from session_Part.Models.Product import Product
from session_Part.Models.Order import Order
from session_Part.Models.CreditCard import CreditCard
from session_Part.Models.Shipping_information import Shipping_information
from session_Part.Models.Transaction import Transaction
from session_Part.Models.BaseModel import BaseModel
from session_Part.inf349 import app


@pytest.fixture
def client():
    test_db = SqliteDatabase(':memory:')

    models = [Product, Order, CreditCard, Shipping_information, Transaction]
    original_dbs = {model: model._meta.database for model in models}

    for model in models:
        model._meta.database = test_db

    test_db.connect()
    test_db.create_tables(models)

    yield app.test_client()

    test_db.drop_tables(models)
    test_db.close()

    for model, db in original_dbs.items():
        model._meta.database = db


@pytest.fixture
def sample_product():
    return Product.create(
        id=1,
        name="Test Product",
        type="Type 1",
        description="Description",
        image="image.jpg",
        height=10,
        weight=100,
        price=1000,
        in_stock=True
    )


@pytest.fixture
def sample_order(sample_product):
    return Order.create(
        product=sample_product,
        quantity=2,
        shipping_price=500,
        total_price=2000,
        total_price_tax=2300
    )


@pytest.fixture
def complete_order(sample_order):
    with Order._meta.database.atomic():
        shipping_info = Shipping_information.create(
            country="Canada",
            address="123 Test St",
            postal_code="G7X 7W7",
            city="Test City",
            province="QC"
        )

        credit_card = CreditCard.create(
            name="John Doe",
            first_digits=4242,
            last_digits=4242,
            expiration_month=12,
            expiration_year=2025
        )

        transaction = Transaction.create(
            id="trans123",
            success=True,
            amount_charged=2500
        )

        Order.update(
            email="test@example.com",
            shipping_information=shipping_info,
            credit_card=credit_card,
            transaction=transaction,
            paid=True
        ).where(Order.id == sample_order.id).execute()

        return Order.get_by_id(sample_order.id)


def test_get_order_not_found(client):
    response = client.get("/order/999")
    assert response.status_code == 404
    assert response.json == {"error": "Commande non trouvée"}


def test_get_basic_order(client, sample_order):
    response = client.get(f"/order/{sample_order.id}")
    assert response.status_code == 200

    data = response.json
    assert "order" in data
    order_data = data["order"]

    assert order_data["id"] == sample_order.id
    assert order_data["product"]["quantity"] == 2
    assert order_data["total_price"] == 2000
    assert order_data["shipping_price"] == 500
    assert order_data["paid"] == False
    assert order_data["email"] is None
    assert order_data["credit_card"] == {}
    assert order_data["shipping_information"] == {}
    assert order_data["transaction"] == {}


def test_get_complete_order(client, complete_order):
    response = client.get(f"/order/{complete_order.id}")
    assert response.status_code == 200

    data = response.json
    assert "order" in data
    order_data = data["order"]

    assert order_data["id"] == complete_order.id
    assert order_data["product"]["quantity"] == 2
    assert order_data["total_price"] == 2000
    assert order_data["shipping_price"] == 500
    assert order_data["paid"] == True
    assert order_data["email"] == "test@example.com"

    shipping_info = order_data["shipping_information"]
    assert shipping_info["country"] == "Canada"
    assert shipping_info["address"] == "123 Test St"
    assert shipping_info["postal_code"] == "G7X 7W7"
    assert shipping_info["city"] == "Test City"
    assert shipping_info["province"] == "QC"

    credit_card = order_data["credit_card"]
    assert credit_card["name"] == "John Doe"
    assert credit_card["first_digits"] == 4242
    assert credit_card["last_digits"] == 4242

    transaction_data = order_data["transaction"]
    assert transaction_data["id"] == "trans123"
    assert transaction_data["success"] == True
    assert transaction_data["amount_charged"] == 2500