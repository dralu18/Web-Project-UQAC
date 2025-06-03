import pytest
from session_Part.inf349 import app
from session_Part.Models.Product import Product
from session_Part.Models.Order import Order
from peewee import SqliteDatabase
from session_Part.ErrorMessage import Error422OrderNeedProduct, Error422OrderDoesNotExist, Error422ProductOutOfInventory


@pytest.fixture
def client():
    test_db = SqliteDatabase(':memory:')

    original_db = Product._meta.database
    original_order_db = Order._meta.database

    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'

    Product._meta.database = test_db
    Order._meta.database = test_db

    test_db.connect()
    test_db.create_tables([Product, Order])

    Product.create(
        id=1,
        name="Produit En Stock",
        type="Type 1",
        description="Description 1",
        image="image1.jpg",
        height=10,
        weight=100,
        price=1000,
        in_stock=True
    )
    Product.create(
        id=2,
        name="Produit Hors Stock",
        type="Type 2",
        description="Description 2",
        image="image2.jpg",
        height=20,
        weight=200,
        price=2000,
        in_stock=False
    )

    yield app.test_client()

    test_db.drop_tables([Product, Order])
    test_db.close()

    Product._meta.database = original_db
    Order._meta.database = original_order_db


def test_create_order_success(client):
    data = {
        "product": {
            "id": 1,
            "quantity": 2
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 302
    assert response.location.startswith("/order/")


def test_create_order_missing_data(client):
    response = client.post("/order", json={})
    assert response.status_code == 422
    assert response.json == Error422OrderNeedProduct[0]


def test_create_order_missing_product_fields(client):
    data = {
        "product": {
            "id": 1
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 422
    assert response.json == Error422OrderNeedProduct[0]


def test_create_order_invalid_quantity(client):
    data = {
        "product": {
            "id": 1,
            "quantity": 0
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 422
    assert response.json == Error422OrderNeedProduct[0]


def test_create_order_product_not_found(client):
    data = {
        "product": {
            "id": 999,
            "quantity": 1
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 422
    assert response.json == Error422OrderDoesNotExist[0]


def test_create_order_product_out_of_stock(client):
    data = {
        "product": {
            "id": 2,
            "quantity": 1
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 422
    assert response.json == Error422ProductOutOfInventory[0]


def test_create_order_calculates_prices(client):
    data = {
        "product": {
            "id": 1,
            "quantity": 2
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 302

    order_id = int(response.location.split('/')[-1])

    order = Order.get_by_id(order_id)
    assert order.total_price == 2000
    assert order.shipping_price == 500


def test_create_order_with_high_weight(client):
    Product.create(
        id=3,
        name="Produit Lourd",
        type="Type 3",
        description="Description 3",
        image="image3.jpg",
        height=30,
        weight=1000,
        price=3000,
        in_stock=True
    )

    data = {
        "product": {
            "id": 3,
            "quantity": 3
        }
    }
    response = client.post("/order", json=data)
    assert response.status_code == 302

    order_id = int(response.location.split('/')[-1])
    order = Order.get_by_id(order_id)
    assert order.shipping_price == 2500