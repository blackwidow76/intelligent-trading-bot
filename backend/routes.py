from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from models import Token, User
from websocket_client import pump_fun_client
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter()

# Define routes
@router.get("/")
async def home():
    return JSONResponse({"message": "Welcome to the Pump.fun API"})

if __name__ == '__main__':
    logger.info("Initializing FastAPI router")
    try:
        client = PumpPortalClient()  # Create an instance of PumpPortalClient
        asyncio.run(client.subscribe_new_token())  # Use the method from the instance
    except Exception as e:
        logger.error(f"Error running the WebSocket client: {str(e)}", exc_info=True)
    logger.info("Running FastAPI router")
