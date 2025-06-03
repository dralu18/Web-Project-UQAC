from peewee import *
from session_Part.Models.BaseModel import BaseModel

class Product(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    type = CharField()
    description = TextField()
    image = CharField()
    height = IntegerField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

    def calculate_weight(self, quantity:int):
        if not isinstance(quantity, int):
            raise TypeError("Quantity must be an integer")
        # Calcul des frais de port
        total_weight = self.weight * quantity
        if total_weight <= 500:
            return 500
        elif total_weight <= 2000:
            return 1000
        else:
            return 2500

