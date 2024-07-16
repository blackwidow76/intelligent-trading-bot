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
    uri = config.PUMPPORTAL_API_URL
    logger.info("Starting Pump.fun WebSocket client")
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to Pump.fun WebSocket")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    # Process and emit the data to connected clients
                    if data.get('event') == 'TOKEN_MINT':
                        socketio.emit('new_mint', data)
                        logger.info(f"Received new mint data: {data}")
                    else:
                        socketio.emit('other_event', data)
                        logger.info(f"Received other event data: {data}")
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection to Pump.fun WebSocket closed. Reconnecting...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error in Pump.fun WebSocket client: {str(e)}", exc_info=True)
            await asyncio.sleep(5)