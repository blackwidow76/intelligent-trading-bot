from pymongo import MongoClient
import os

from database.database import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_default_database()

from mongoengine import Document, StringField, IntField, FloatField, DateTimeField

class Token(Document):
    name = StringField(required=True, max_length=80)
    symbol = StringField(required=True, max_length=10)
    launch_date = DateTimeField(required=True)
    price = FloatField(required=True)
    volume = FloatField()
    contract_address = StringField(unique=True, required=True)

class Trade(Document):
    token = StringField(required=True)
    trade_time = DateTimeField(required=True)
    amount = FloatField(required=True)
    price = FloatField(required=True)

class User(Document):
    username = StringField(unique=True, required=True)
    email = StringField(unique=True, required=True)
