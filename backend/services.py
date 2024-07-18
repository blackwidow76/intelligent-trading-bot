import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure MongoDB URI is set
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    logger.error("MONGODB_URI is not set in the environment variables.")
    exit(1)  # Exit if no MongoDB URI is provided

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client.get_database('pumpportal')

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def home():
    return JSONResponse({"message": "Welcome to the Pump.fun API"})

class Token:
    def __init__(self, contract_address):
        self.contract_address = contract_address

    def to_dict(self):
        return {"contract_address": self.contract_address}

@app.post("/add_token")
async def add_token(request: Request):
    form = await request.form()
    contract_address = form.get('contract_address')
    
    # Ensure MongoDB is initialized properly
    if not db:
        logger.error("MongoDB has not been initialized correctly.")
        raise HTTPException(status_code=500, detail="MongoDB initialization failed")

    # Use the database object safely after initialization check
    token = Token(contract_address)
    if 'tokens' not in db.list_collection_names():
        db.create_collection('tokens')
    db.tokens.insert_one(token.to_dict())
    return JSONResponse({"message": "Token added"}, status_code=200)

if __name__ == '__main__':
    import uvicorn
    logger.info("Initializing FastAPI app")
    uvicorn.run(app, host="0.0.0.0", port=8080)
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
