from peewee import *
from db import db

class BaseModel(Model):
    class Meta:
        database = db