import asyncio
import websockets
import json
import logging
from flask_socketio import SocketIO
from config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socketio = SocketIO()

# WebSocket client to connect to Pump.fun
async def pump_fun_client():
    uri = "wss://pumpportal.fun/api/data"
    logger.info("Starting Pump.fun WebSocket client")
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to Pump.fun WebSocket")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    # Process and emit the data to connected clients
                    from handlers import handle_new_token_event, handle_trade_event

                    if data.get('event') == 'newToken':
                        await handle_new_token_event(data)
                        logger.info(f"Received new token data: {data}")
                    elif data.get('event') == 'trade':
                        await handle_trade_event(data)
                        logger.info(f"Received trade data: {data}")
                    async def store_new_token_data(data):
                        # Implement logic to store new token data in the database
                        pass

                    async def store_trade_data(data):
                        # Implement logic to store trade data in the database
                        pass
                    # Store relevant information in the database
                    if data.get('event') == 'newToken':
                        await store_new_token_data(data)
                    elif data.get('event') == 'trade':
                        await store_trade_data(data)
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection to Pump.fun WebSocket closed. Reconnecting...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error in Pump.fun WebSocket client: {str(e)}", exc_info=True)
            await asyncio.sleep(5)
