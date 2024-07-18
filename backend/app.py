# Import load_dotenv from dotenv at the top of your file
from dotenv import load_dotenv

# Immediately call load_dotenv to load environment variables from .env file
load_dotenv()

from flask import Flask, jsonify, request
import logging
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from .config import Config


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

app = Flask(__name__)                                                             
app.config.from_object(Config)                                                    
                                                                                      
# Set the MONGO_URI in the Flask config                                           
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.6'  # Replace with your actual Mongo 
URI                                                                               
          
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure MongoDB URI is set
if not app.config.get("MONGODB_URI"):
    logger.error("MONGODB_URI is not set in the configuration.")
    exit(1)  # Exit if no MongoDB URI is provided

mongo = PyMongo(app)

# Debugging to check mongo initialization
if not hasattr(mongo, 'db'):
    logger.error("MongoDB has not been initialized correctly.")
    exit(1)
    exit(1)  # Exit if MongoDB initialization fails


socketio = SocketIO(app)

# Define routes
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Pump.fun API"})

class Token:
    def __init__(self, contract_address):
        self.contract_address = contract_address

    def to_dict(self):
        return {"contract_address": self.contract_address}

@app.route('/add_token', methods=['POST'])
def add_token():
    contract_address = request.form['contract_address']
    
    # Ensure MongoDB is initialized properly
    if not mongo or not hasattr(mongo, 'db'):
        logger.error("MongoDB has not been initialized correctly.")
        exit(1)

    # Use the database object safely after initialization check
    token = Token(contract_address)
    if 'tokens' not in mongo.db.list_collection_names():
        mongo.db.create_collection('tokens')
    mongo.db.tokens.insert_one(token.to_dict())
    return 'Token added', 200


import asyncio  # Add import for asyncio

if __name__ == '__main__':
    logger.info("Initializing Flask app")