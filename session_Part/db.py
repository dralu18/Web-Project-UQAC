import os

from peewee import SqliteDatabase

db = SqliteDatabase(os.path.join(os.path.dirname(__file__), 'Bat_File', 'shop.db'))