from peewee import *
from Models.BaseModel import BaseModel
from Models.Product import Product
from Models.Shipping_information import Shipping_information
from Models.Transaction import Transaction
from Models.CreditCard import CreditCard
import json
import re

class Order(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref="orders")
    quantity = IntegerField()
    paid = BooleanField(default=False)
    email = TextField(null=True)
    shipping_price = FloatField()
    total_price = FloatField(null=True)
    total_price_tax = FloatField(null=True)
    credit_card = ForeignKeyField(CreditCard, backref="orders", null=True, default=None)
    shipping_information = ForeignKeyField(Shipping_information, backref="orders", null=True, default=None)
    transaction = ForeignKeyField(Transaction, backref="orders", null=True, default=None)

    def load_object_to_json(self):
        return {
                   "order": {
                       "id": self.id,
                       "total_price": self.total_price,
                       "total_price_tax": self.total_price_tax,
                       "email": self.email,
                       "credit_card": self.credit_card.load_object_to_json() if self.credit_card is not None else {},
                       "shipping_information": self.shipping_information.load_object_to_json() if self.shipping_information is not None else {},
                       "transaction": self.transaction.load_object_to_json() if self.transaction is not None else {},
                       "paid": self.paid,
                       "product": {
                           "id": self.product.id,
                           "quantity": self.quantity
                       },
                       "shipping_price": self.shipping_price
                   }
               }

    def is_valid_email(self, ctrEmail: str) -> bool:
        if not isinstance(ctrEmail, str):
            return False

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        return re.match(email_regex, ctrEmail) is not None

    def is_valid_province(self, ctrProvince: str) -> bool:
        if not isinstance(ctrProvince, str):
            return False

        valid_provinces = {"QC", "ON", "AB", "BC", "NS"}
        return ctrProvince.upper() in valid_provinces