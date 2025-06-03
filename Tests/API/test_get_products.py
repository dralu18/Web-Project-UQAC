import pytest
from flask import Flask
from session_Part.Models.Product import Product
from session_Part.inf349 import app
from peewee import SqliteDatabase
import json


@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def sample_products():
    # Création d'une base de données en mémoire pour les tests
    test_db = SqliteDatabase(':memory:')
    Product._meta.database = test_db
    test_db.connect()
    test_db.create_tables([Product])

    # Création de produits de test
    products = [
        Product.create(
            id=1,
            name="Produit Test 1",
            type="Type 1",
            description="Description 1",
            image="image1.jpg",
            height=10,
            weight=100,
            price=1000,
            in_stock=True
        ),
        Product.create(
            id=2,
            name="Produit Test 2",
            type="Type 2",
            description="Description 2",
            image="image2.jpg",
            height=20,
            weight=200,
            price=2000,
            in_stock=False
        )
    ]

    yield products

    # Nettoyage
    test_db.drop_tables([Product])
    test_db.close()


def test_get_products_status(client, sample_products):
    """Test que la route retourne bien un code 200"""
    response = client.get("/")
    assert response.status_code == 200


def test_get_products_content_structure(client, sample_products):
    """Test la structure de la réponse JSON"""
    response = client.get("/")
    data = json.loads(response.data)

    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) == 2


def test_get_products_fields(client, sample_products):
    """Test que chaque produit contient tous les champs requis"""
    response = client.get("/")
    data = json.loads(response.data)

    required_fields = ["id", "name", "description", "image", "weight", "price", "in_stock"]

    for product in data["products"]:
        for field in required_fields:
            assert field in product


def test_get_products_values(client, sample_products):
    """Test que les valeurs des produits sont correctes"""
    response = client.get("/")
    data = json.loads(response.data)

    # Vérification du premier produit
    product1 = data["products"][0]
    assert product1["id"] == 1
    assert product1["name"] == "Produit Test 1"
    assert product1["description"] == "Description 1"
    assert product1["image"] == "image1.jpg"
    assert product1["weight"] == 100
    assert product1["price"] == 1000
    assert product1["in_stock"] == True


def test_get_products_empty_db(client):
    """Test le comportement avec une base de données vide"""
    # Création d'une base de données vide
    test_db = SqliteDatabase(':memory:')
    Product._meta.database = test_db
    test_db.connect()
    test_db.create_tables([Product])

    response = client.get("/")
    data = json.loads(response.data)

    assert response.status_code == 200
    assert "products" in data
    assert len(data["products"]) == 0

    test_db.close()
