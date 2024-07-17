from service.App import App
from pymongo import MongoClient

try:
    MONGODB_URI = App.config["MONGODB_URI"]
except KeyError:
    MONGODB_URI = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.6" # Default to local MongoDB instance

client = MongoClient(MONGODB_URI)
db = client.get_database('mongo')  # Replace 'default_db_name' with the actual default database name
