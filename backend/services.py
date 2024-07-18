import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from dotenv import load_dotenv
from models import Token, User

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

@app.post("/add_token")
async def add_token(request: Request):
    data = await request.json()
    new_token = Token(**data)
    db.tokens.insert_one(new_token.dict())
    return JSONResponse({"message": "Token added successfully"}, status_code=201)

@app.post("/add_user")
async def add_user(request: Request):
    data = await request.json()
    new_user = User(**data)
    db.users.insert_one(new_user.dict())
    return JSONResponse({"message": "User added successfully"}, status_code=201)

if __name__ == '__main__':
    import uvicorn
    logger.info("Initializing FastAPI app")
    uvicorn.run(app, host="0.0.0.0", port=8080)
