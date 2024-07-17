import os
import logging
import asyncio
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from database.database import MONGODB_URI
from websocket_client import pump_fun_client, socketio

# Initialize Flask app
app = Flask(__name__)
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI')
app.config['MONGODB_DBNAME'] = 'pumpportal'
db = MONGODB_URI(os.getenv('MONGODB_URI'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define SQLAlchemy models
class Token(db.Document):
    id = db.IntField(primary_key=True)
    name = db.StringField(required=True)
    symbol = db.StringField(required=True)
    launch_date = db.DateTimeField(required=True)

    def __init__(self, name, symbol, launch_date):
        self.name = name
        self.symbol = symbol
        self.launch_date = launch_date

class User(db.Document):
    id = db.IntField(primary_key=True)
    username = db.StringField(required=True)
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
    new_token = Token(name=data['name'], symbol=data['symbol'], launch_date=data['launch_date'])
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

# Define a processing function for the data received from the WebSocket
def process_data(data):
    # Implement your data processing logic here
    pass

if __name__ == '__main__':
    logger.info("Initializing Flask app")
    try:
        # Specify the URI and method for the WebSocket connection
        uri = "wss://pumpportal.fun/api/data"
        method = "GET"
        asyncio.run(pump_fun_client(uri, method, process_data))
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running Flask app with SocketIO")
    socketio.init_app(app)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, use_reloader=False, log_output=True)