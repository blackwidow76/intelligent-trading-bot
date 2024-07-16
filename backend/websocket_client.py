import asyncio
import websockets
import json
import logging
from flask_socketio import SocketIO
from .config import Config
from backend.models import db, Token
from database.models import Trade  # Adjusted import path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socketio = SocketIO()

# WebSocket client to connect to Pump.fun
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
            await process_data(data)

async def store_new_token_mint_data(data):
    new_token = Token()
    new_token.contract_address = data['contract_address']
    db.session.add(new_token)
    db.session.commit()

async def fetch_and_store_token_metadata(contract_address):
    # Assuming fetch_token_metadata is defined in pumpportal/pumpportal_client.py
    from pumpportal.pumpportal_client import fetch_token_metadata
    metadata = await fetch_token_metadata(contract_address)
    token = Token.query.filter_by(contract_address=contract_address).first()
    if token:
        token.name = metadata['name']
        token.symbol = metadata['symbol']
        token.launch_date = metadata['launch_date']
        token.price = metadata['price']
        token.volume = metadata['volume']
        db.session.commit()

async def store_trade_data(data):
    new_trade = Trade(
        token_id=data['token_id'],
        trade_time=data['trade_time'],
        amount=data['amount'],
        price=data['price']
    )
    db.session.add(new_trade)
    db.session.commit()

async def process_data(data):
    try:
        if data.get('event') == 'newTokenMint':
            await store_new_token_mint_data(data)
        elif data.get('event') == 'trade':
            await store_trade_data(data)
        elif data.get('event') == 'mevBotTransaction':
            # Assuming mev_bot is defined in backend/mev_bot.py
            from backend.mev_bot import MEVBot
            # Assuming solana_client and bitquery_client are initialized somewhere
            from solana.rpc.api import Client as SolanaClient
            from bitquery import Bitquery
            solana_client = SolanaClient()  # Initialize or import the actual instance
            bitquery_client = Bitquery()  # Initialize or import the actual instance
            mev_bot = MEVBot(solana_client, bitquery_client)
            await mev_bot.execute_transaction(data)
    except websockets.exceptions.ConnectionClosed:
        logger.error("Connection to Pump.fun WebSocket closed. Reconnecting...")
        await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"Error in Pump.fun WebSocket client: {str(e)}", exc_info=True)
        await asyncio.sleep(5)

# Entry point to start the WebSocket client
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pump_fun_client())
