from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from service.App import App

from pymongo import MongoClient

try:
    MONGODB_URI = App.config["MONGODB_URI"]
except KeyError:
    MONGODB_URI = "mongodb://localhost:27017/"  # Default to local MongoDB instance

client = MongoClient(MONGODB_URI)
db = client.get_database()
