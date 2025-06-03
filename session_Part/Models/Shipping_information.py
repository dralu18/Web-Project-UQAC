from peewee import *
from session_Part.Models.BaseModel import BaseModel

class Shipping_information(BaseModel):
    id = AutoField()
    country = TextField(null=True)
    address = TextField(null=True)
    postal_code = TextField(null=True)
    city = TextField(null=True)
    province = TextField(null=True)

    @classmethod
    def from_dict(cls, shipping_info: dict):
        return cls(
            country=shipping_info.get("country"),
            address=shipping_info.get("address"),
            postal_code=shipping_info.get("postal_code"),
            city=shipping_info.get("city"),
            province=shipping_info.get("province")
        )

    def load_object_to_json(self):
        return {
            "country": self.country,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "province": self.province,
        }

