from flask import Flask, jsonify, request
from pumpportal.pumpportal_client import PumpPortalClient
import logging
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from .config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure MongoDB URI is set
if not app.config.get("MONGO_URI"):
    logger.error("MONGO_URI is not set in the configuration.")
    exit(1)  # Exit if no MongoDB URI is provided

mongo = PyMongo(app)

# Debugging to check mongo initialization
if not hasattr(mongo, 'db'):
    logger.error("MongoDB has not been initialized correctly.")
    exit(1)

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
    token = Token(contract_address)
    if 'tokens' not in mongo.db.list_collection_names():
        mongo.db.create_collection('tokens')
    mongo.db.tokens.insert_one(token.to_dict())
    return 'Token added', 200


from tests.test_pumpfun_integration import test_pumpfun_integration
from tests.test_jito_integration import test_jito_integration

import asyncio  # Add import for asyncio

if __name__ == '__main__':
    logger.info("Initializing Flask app")
    # Add testing logic here
    test_pumpfun_integration()
    test_jito_integration()
    try:
        from pumpportal.pumpportal_client import PumpPortalClient
        client = PumpPortalClient()
        asyncio.run(client.subscribe_new_token())
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running Flask app with SocketIO")
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, use_reloader=False, log_output=True)
