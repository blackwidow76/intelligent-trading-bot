from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from pumpportal.pumpportal_client import PumpPortalClient
from .config import Config
from pymongo import MongoClient
import os
import logging
import asyncio
from flask_socketio import SocketIO

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
db = MongoClient(os.getenv('MONGO_URI')) # Initialize SQLAlchemy with the app
socketio = SocketIO(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define SQLAlchemy models
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    launch_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)

    def __init__(self, name, symbol, launch_date, price, volume):
        self.name = name
        self.symbol = symbol
        self.launch_date = launch_date
        self.price = price
        self.volume = volume

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Define routes
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Pump.fun API"})


from tests.test_pumpfun_integration import test_pumpfun_integration
from tests.test_jito_integration import test_jito_integration

if __name__ == '__main__':
    logger.info("Initializing Flask app")
    # Add testing logic here
    test_pumpfun_integration()
    test_jito_integration()
    try:
        client = PumpPortalClient()
        asyncio.run(client.subscribe_new_token())
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running Flask app with SocketIO")
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, use_reloader=False, log_output=True)
