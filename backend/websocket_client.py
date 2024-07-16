import asyncio
import websockets.client  # Ensure correct import
import json
import logging
from flask_socketio import SocketIO
from .config import Config
from backend.models import db, Token
from database.models import Trade  # Adjusted import path
from pumpportal.pumpportal_client import fetch_token_metadata  # Ensure correct import path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

socketio = SocketIO()

# WebSocket client to connect to Pump.fun
async def pump_fun_client():
    uri = "wss://pumpportal.fun/api/data"
    logger.info("Starting Pump.fun WebSocket client")
    async with websockets.client.connect(uri) as websocket:  # Use websockets.client.connect
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


async def process_data(data):
    try:
        if data.get('txType') == 'create':
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
        elif data.get('txType') == 'create':
            # Additional fields to handle
            mint = data.get('mint')
            trader_public_key = data.get('traderPublicKey')
            initial_buy = data.get('initialBuy')
            bonding_curve_key = data.get('bondingCurveKey')
            v_tokens_in_bonding_curve = data.get('vTokensInBondingCurve')
            v_sol_in_bonding_curve = data.get('vSolInBondingCurve')
            market_cap_sol = data.get('marketCapSol')
            # Log or process these fields as needed
            logger.info(f"New token mint data: {mint}, {trader_public_key}, {initial_buy}, {bonding_curve_key}, {v_tokens_in_bonding_curve}, {v_sol_in_bonding_curve}, {market_cap_sol}")
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
