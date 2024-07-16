import asyncio
import websockets
import json
import logging
from flask_socketio import SocketIO
from .config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socketio = SocketIO()

# WebSocket client to connect to Pump.fun
import json

async def pump_fun_client():
    uri = "wss://pumpportal.fun/api/data"
    logger.info("Starting Pump.fun WebSocket client")
    async with websockets.connect(uri) as websocket:
        logger.info("Connected to Pump.fun WebSocket")
        
        # Subscribing to token creation events
        payload = {
            "method": "subscribeNewToken",
        }
        await websocket.send(json.dumps(payload))

        # Subscribing to trades made by accounts
        payload = {
            "method": "subscribeAccountTrade",
            "keys": ["AArPXm8JatJiuyEffuC1un2Sc835SULa4uQqDcaGpAjV"]  # array of accounts to watch
        }
        await websocket.send(json.dumps(payload))

        # Subscribing to trades on tokens
        payload = {
            "method": "subscribeTokenTrade",
            "keys": ["91WNez8D22NwBssQbkzjy4s2ipFrzpmn5hfvWVe2aY5p"]  # array of token CAs to watch
        }
        await websocket.send(json.dumps(payload))
        
        async for message in websocket:
            data = json.loads(message)
            logger.info(f"Received data: {data}")
                    from backend.models import db, Token, Trade

                    async def store_new_token_data(data):
                        new_token = Token(
                            name=data['name'],
                            symbol=data['symbol'],
                            launch_date=data['launch_date'],
                            price=data['price'],
                            volume=data['volume']
                        )
                        db.session.add(new_token)
                        await db.session.commit()

                    async def store_trade_data(data):
                        new_trade = Trade(
                            token_id=data['token_id'],
                            trade_time=data['trade_time'],
                            amount=data['amount'],
                            price=data['price']
                        )
                        db.session.add(new_trade)
                        await db.session.commit()
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
