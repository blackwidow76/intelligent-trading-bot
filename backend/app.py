# Import load_dotenv from dotenv at the top of your file
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
    try:
        client.server_info()  # Attempt to retrieve server information
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
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
    
    # Trigger the data stream
    from backend.services import start_data_stream
    start_data_stream()
