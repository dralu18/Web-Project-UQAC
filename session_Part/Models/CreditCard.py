from peewee import *
from session_Part.Models.BaseModel import BaseModel

class CreditCard(BaseModel):
    id = AutoField()
    name = CharField()
    first_digits = IntegerField()
    last_digits = IntegerField()
    expiration_year = IntegerField()
    expiration_month = IntegerField()

    @classmethod
    def from_dict(cls, CreditCard_info: dict):
        return cls(
            name=CreditCard_info.get("name"),
            first_digits=CreditCard_info.get("first_digits"),
            last_digits=CreditCard_info.get("last_digits"),
            expiration_year=CreditCard_info.get("expiration_year"),
            expiration_month=CreditCard_info.get("expiration_month")
        )

    def load_object_to_json(self):
        return {
            "name": self.name,
            "first_digits": self.first_digits,
            "last_digits": self.last_digits,
            "expiration_year": self.expiration_year,
            "expiration_month": self.expiration_month
        }