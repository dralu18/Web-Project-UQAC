from peewee import *
from Models.BaseModel import BaseModel

class Shipping_information(BaseModel):
    id = AutoField()
    country = TextField(null=True)
    address = TextField(null=True)
    postal_code = TextField(null=True)
    city = TextField(null=True)
    province = TextField(null=True)

    def __init__(self, shipping_info: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if shipping_info:
            self.country = shipping_info.get("country")
            self.address = shipping_info.get("address")
            self.postal_code = shipping_info.get("postal_code")
            self.city = shipping_info.get("city")
            self.province = shipping_info.get("province")

    def load_object_to_json(self):
        return {
            "country": self.country,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "province": self.province,
        }

