import pytest
from flask import Flask
from session_Part.inf349 import app, db
from session_Part.Models.Product import Product
from peewee import SqliteDatabase


@pytest.fixture
def client():
    # Configuration de la base de données de test
    test_db = SqliteDatabase(':memory:')

    # Sauvegarde la base de données originale
    original_db = Product._meta.database

    # Configuration de l'application pour les tests
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'

    # Changement de la base de données pour les tests
    Product._meta.database = test_db

    # Création des tables et des données de test
    test_db.connect()
    test_db.create_tables([Product])

    # Création de produits de test
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
    )
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

    yield app.test_client()

    # Nettoyage
    test_db.drop_tables([Product])
    test_db.close()

    # Restauration de la base de données originale
    Product._meta.database = original_db


def test_get_products(client):
    """Test de la route GET / pour la liste des produits"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) == 2


def test_get_products_content(client):
    """Test du contenu des produits retournés"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()

    # Vérification qu'il y a des produits
    assert len(data["products"]) > 0

    # Vérification du premier produit
    product = data["products"][0]
    assert "id" in product
    assert "name" in product
    assert "description" in product
    assert "price" in product
    assert "weight" in product
    assert "in_stock" in product
    assert "image" in product

    # Vérification des valeurs du premier produit
    assert product["id"] == 1
    assert product["name"] == "Produit Test 1"
    assert product["description"] == "Description 1"
    assert product["price"] == 1000
    assert product["weight"] == 100
    assert product["in_stock"] == True
    assert product["image"] == "image1.jpg"
