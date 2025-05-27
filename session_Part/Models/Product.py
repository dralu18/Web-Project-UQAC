from peewee import *
from Models.BaseModel import BaseModel

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

