import json
from urllib.request import urlopen
from session_Part.Models.Product import Product
from session_Part.db import db

def fetch_and_store_products():
    url = "https://dimensweb.uqac.ca/~jgnault/shops/products/"

    try:
        with urlopen(url) as response:
            data = json.loads(response.read().decode())

            with db.atomic():
                for prod in data.get("products", []):
                    Product.insert(
                        id=prod["id"],
                        name=prod["name"],
                        type=prod["type"],
                        description=prod["description"],
                        image=prod["image"],
                        height=prod["height"],
                        weight=prod["weight"],
                        price=prod["price"],
                        in_stock=prod["in_stock"]

                    ).on_conflict_replace().execute()

        print("Produits insérés avec succès.")

    except Exception as e:
        print("Erreur lors de la récupération ou de l'insertion des produits :", e)