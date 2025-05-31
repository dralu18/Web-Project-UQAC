from peewee import *
from Models.BaseModel import BaseModel
from Models.Product import Product
from Models.Shipping_information import Shipping_information
import json

class Order(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref="orders")
    quantity = IntegerField()
    paid = BooleanField(default=False)
    email = TextField(null=True)
    shipping_price = FloatField()
    total_price = FloatField(null=True)
    total_price_tax = FloatField(null=True)
    credit_card = TextField(null=True)
    shipping_information = ForeignKeyField(Shipping_information, backref="orders", null=True, default=None)
    transaction = TextField(null=True)
