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


if __name__ == '__main__':
    logger.info("Initializing Flask app")
    try:
        client = PumpPortalClient()  # Create an instance of PumpPortalClient
        asyncio.run(client.subscribe_new_token())  # Use the method from the instance
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running Flask app with SocketIO")
    socketio.init_app(app)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, use_reloader=False, log_output=True)