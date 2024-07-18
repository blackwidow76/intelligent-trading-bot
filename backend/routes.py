from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from models import Token, User
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Define routes
@app.get("/")
async def home():
    return JSONResponse({"message": "Welcome to the Pump.fun API"})

@app.get("/tokens")
async def get_tokens():
    tokens = Token.objects.all()
    return JSONResponse([token.to_dict() for token in tokens])

@app.post("/tokens")
async def add_token(request: Request):
    data = await request.json()
    new_token = Token(**data)
    new_token.save()
    return JSONResponse({"message": "Token added successfully"}, status_code=201)

@app.get("/users")
async def get_users():
    users = User.objects.all()
    return JSONResponse([user.to_dict() for user in users])

@app.post("/users")
async def add_user(request: Request):
    data = await request.json()
    new_user = User(**data)
    new_user.save()
    return JSONResponse({"message": "User added successfully"}, status_code=201)
