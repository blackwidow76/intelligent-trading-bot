from flask import jsonify, request
from app import app, socketio  # Updated to use relative import
from models import db, Token, User
from websocket_client import pump_fun_client
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    new_token = Token()
    new_token.name = data['name']
    new_token.symbol = data['symbol']
    new_token.launch_date = data['launch_date']
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
    try:
        asyncio.run(pump_fun_client())
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running Flask app with SocketIO")
    socketio.init_app(app)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, use_reloader=False, log_output=True)