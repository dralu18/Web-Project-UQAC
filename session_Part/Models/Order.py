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

    def load_object_to_json(self):
        return {
                   "order": {
                       "id": self.id,
                       "total_price": self.total_price,
                       "total_price_tax": self.total_price_tax,
                       "email": self.email,
                       "credit_card": json.loads(self.credit_card) if self.credit_card else {},
                       "shipping_information": Shipping_information.get(Shipping_information.id == self.shipping_information).load_object_to_json() if self.shipping_information is not None else {},
                       "transaction": json.loads(self.transaction) if self.transaction else {},
                       "paid": self.paid,
                       "product": {
                           "id": self.product.id,
                           "quantity": self.quantity
                       },
                       "shipping_price": self.shipping_price
                   }
               }
