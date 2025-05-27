from peewee import *
from Models.BaseModel import BaseModel
from Models.Product import Product
import json

class Order(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref="orders")
    quantity = IntegerField()
    paid = BooleanField(default=False)
    email = TextField(null=True)
    shipping_price = IntegerField(null=True)
    total_price = IntegerField(null=True)
    total_price_tax = FloatField(null=True)
    credit_card = TextField(null=True)
    shipping_information = TextField(null=True)
    transaction = TextField(null=True)



#200 OK
#{ "order" :
#   {
#       "id" : 6543,
#       "total_price" : 9148,
#       "total_price_tax" : 10520.20,
#       "email" : null,
#       "credit_card": {},
#       "shipping_information" : {},
#       "paid": false,
#       "transaction": {},
#       "product" : {
#           "id" : 123,
#           "quantity" : 1 },
#       "shipping_price" : 1000 }
#    }