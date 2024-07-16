from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .websocket_client import pump_fun_client, socketio  # Ensure this matches the correct file name
from .config import Config
import os
import logging
import asyncio

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

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

@app.route("/tokens", methods=["GET"])
def get_tokens():
    tokens = Token.query.all()
    return jsonify([{"id": token.id, "name": token.name, "symbol": token.symbol, "launch_date": token.launch_date} for token in tokens])

@app.route("/tokens", methods=["POST"])
def add_token():
    data = request.get_json()
    new_token = Token(name=data['name'], symbol=data['symbol'], launch_date=data['launch_date'], price=data['price'], volume=data['volume'])
    db.session.add(new_token)
    db.session.commit()
    return jsonify({"message": "Token added successfully"}), 201

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users])

@app.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    new_user = User()
    new_user.username = data['username']
    new_user.email = data['email']
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully"}), 201

if __name__ == '__main__':
    logger.info("Initializing Flask app")
    # Add testing logic here
    test_pumpfun_integration()
    test_jito_integration()
    try:
        asyncio.run(pump_fun_client())
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running Flask app with SocketIO")
    socketio.init_app(app)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, use_reloader=False, log_output=True)
