from flask_pymongo import PyMongo
from pymongo import MongoClient
import os

client = MongoClient(os.getenv('MONGODB_URI'))
db = client.get_default_database()

db = client.get_database('pumpportal')  # Replace 'your_database_name' with the actual database name 

from bson import ObjectId
from datetime import datetime

class Token:
    def __init__(self, contract_address, creation_time=None):
        self.contract_address = contract_address
        self.creation_time = creation_time if creation_time else datetime.utcnow()
        self._id = ObjectId()

    def to_dict(self):
        return {
            "_id": self._id,
            "contract_address": self.contract_address,
            "creation_time": self.creation_time
        }