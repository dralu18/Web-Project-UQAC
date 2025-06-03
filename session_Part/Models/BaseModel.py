from peewee import *
from session_Part.db import db

class BaseModel(Model):
    class Meta:
        database = db