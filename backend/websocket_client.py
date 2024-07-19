import asyncio
import websockets
import json
import logging
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from database.models import Token, Trade
import aiohttp
from pymongo import MongoClient
from dotenv import load_dotenv
from service.App import App
import requests

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.6")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.pumpportal  # Replace 'your_database_name' with the actual database name

class PumpPortalClient:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_url = App.config["pumpportal"]["api_url"]
        self.websocket_url = App.config["pumpportal"]["websocket_url"]
        self.public_key = App.config["pumpportal"]["public_key"]
        self.private_key = App.config["pumpportal"]["private_key"]
        self.token_metadata_url = os.getenv("PUMPPORTAL_TOKEN_METADATA_URL")

    async def create_wallet(self):
        response = requests.get(f"{self.api_url}/create-wallet")
        data = response.json()
        return data

    async def subscribe_new_token(self):
        await pump_fun_client(self.websocket_url, "subscribeNewToken", process_data)

    async def fetch_token_metadata(self, contract_address):
        token_metadata_url = f"{self.token_metadata_url}/{contract_address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(token_metadata_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": "Failed to fetch token metadata"}

    async def store_token_data(self, event, metadata):
        tokens_collection = db.tokens  # Assuming 'tokens' is the collection name
        try:
            token_document = {
                "contract_address": event["event"]["contractAddress"],
                "creation_time": event["event"]["timestamp"],
                "token_id": event["event"]["tokenId"],
                "owner": event["event"]["owner"],
                "metadata": metadata,
                "event_type": event["event"]["type"]
            }
            await tokens_collection.insert_one(token_document)
            # Further processing and inserting related data
        except Exception as e:
            logger.error(f"An error occurred while storing token data: {e}")

        # Further processing and inserting related data
        await store_trade_data(event)

    async def subscribe_account_trade(self, accounts):
        await pump_fun_client(self.websocket_url, "subscribeAccountTrade", process_data, keys=accounts)

    async def subscribe_token_trade(self, tokens):
        await pump_fun_client(self.websocket_url, "subscribeTokenTrade", process_data, keys=tokens)

    async def trade(self, action, mint, amount, denominated_in_sol, slippage, priority_fee, pool):
        data = {
            "publicKey": self.public_key,
            "action": action,
            "mint": mint,
            "amount": amount,
            "denominatedInSol": str(denominated_in_sol).lower(),
            "slippage": slippage,
            "priorityFee": priority_fee,
            "pool": pool
        }
        response = requests.post(f"{self.api_url}/trade-local", data=data)
        return response.content
    async def process_data(self, data):
        # Deferred import to avoid circular dependency
        try:
            from backend.mev_bot import MEVBot
            from solana.rpc.api import Client as SolanaClient
            from bitquery.client import BitqueryClient  # Corrected import path
        except ImportError as e:
            logger.error(f"Import error: {e}")
            raise

        solana_rpc_url = "https://api.mainnet-beta.solana.com"
        bitquery_api_key = os.getenv("BITQUERY_API_KEY")

        if not bitquery_api_key:
            logger.error("BITQUERY_API_KEY environment variable not set")
            raise EnvironmentError("BITQUERY_API_KEY environment variable not set")

        solana_client = SolanaClient(solana_rpc_url)  # Provide the Solana RPC URL
        bitquery_client = BitqueryClient(api_key=bitquery_api_key)  # Initialize Bitquery client with API key
        mev_bot = MEVBot(solana_client, bitquery_client)
        await mev_bot.execute_transaction(data)

        # Further processing and inserting related data
        await pump_fun_client("wss://pumpportal.fun/api/data", "subscribeNewToken", process_data)

# Rename the second PumpPortalClient class to a different name
class PumpPortalClientV2:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_url = App.config["pumpportal"]["api_url"]
        self.websocket_url = App.config["pumpportal"]["websocket_url"]
        self.public_key = App.config["pumpportal"]["public_key"]
        self.private_key = App.config["pumpportal"]["private_key"]
        self.token_metadata_url = os.getenv("PUMPPORTAL_TOKEN_METADATA_URL")

    async def create_wallet(self):
        response = requests.get(f"{self.api_url}/create-wallet")
        data = response.json()
        return data

    async def subscribe_new_token(self):
        await pump_fun_client(self.websocket_url, "subscribeNewToken", process_data)

    async def fetch_token_metadata(self, contract_address):
        token_metadata_url = f"{self.token_metadata_url}/{contract_address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(token_metadata_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": "Failed to fetch token metadata"}

    async def store_token_data(self, event, metadata):
        tokens_collection = db.tokens  # Assuming 'tokens' is the collection name
        try:
            token_document = {
                "contract_address": event["event"]["contractAddress"],
                "creation_time": event["event"]["timestamp"],
                "token_name": event["event"].get("tokenName"),
                "token_symbol": event["event"].get("tokenSymbol"),
                "decimals": event["event"].get("decimals"),
                "total_supply": event["event"].get("totalSupply"),
                "owner": event["event"].get("owner"),
                "block_number": event["event"].get("blockNumber"),
                "transaction_hash": event["event"].get("transactionHash")
            }
            await tokens_collection.insert_one(token_document)
            # Further processing and inserting related data
        except Exception as e:
            logger.error(f"An error occurred while storing token data: {e}")

    async def subscribe_account_trade(self, accounts):
        await pump_fun_client(self.websocket_url, "subscribeAccountTrade", process_data, keys=accounts)

    async def subscribe_token_trade(self, tokens):
        await pump_fun_client(self.websocket_url, "subscribeTokenTrade", process_data, keys=tokens)

    async def trade(self, action, mint, amount, denominated_in_sol, slippage, priority_fee, pool):
        data = {
            "publicKey": self.public_key,
            "action": action,
            "mint": mint,
            "amount": amount,
            "denominatedInSol": str(denominated_in_sol).lower(),
            "slippage": slippage,
            "priorityFee": priority_fee,
            "pool": pool
        }
        response = requests.post(f"{self.api_url}/trade-local", data=data)
        return response.content

    async def process_data(self, data):
        # Deferred import to avoid circular dependency
        try:
            from backend.mev_bot import MEVBot
            from solana.rpc.api import Client as SolanaClient
            from bitquery.client import BitqueryClient  # Corrected import path
        except ImportError as e:
            logger.error(f"Import error: {e}")
            raise

        solana_rpc_url = "https://api.mainnet-beta.solana.com"
        bitquery_api_key = os.getenv("BITQUERY_API_KEY")

        if not bitquery_api_key:
            logger.error("BITQUERY_API_KEY environment variable not set")
            raise EnvironmentError("BITQUERY_API_KEY environment variable not set")

        solana_client = SolanaClient(solana_rpc_url)  # Provide the Solana RPC URL
        bitquery_client = BitqueryClient(api_key=bitquery_api_key)  # Initialize Bitquery client with API key
        mev_bot = MEVBot(solana_client, bitquery_client)
        await mev_bot.execute_transaction(data)

async def pump_fun_client(uri, method, process_data_func, keys=None):
    logger.info("Starting Pump.fun WebSocket client")
    retry_interval = 5  # Initial retry interval in seconds
    max_retries = 10  # Maximum number of retries before giving up

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to Pump.fun WebSocket")
                
                payload = {
                    "method": method,
                }
                if keys:
                    payload["keys"] = keys
                await websocket.send(json.dumps(payload))

                # Keep-alive mechanism
                keep_alive_interval = 30  # seconds
                last_heartbeat = asyncio.get_event_loop().time()
                
                while True:
                    if asyncio.get_event_loop().time() - last_heartbeat > keep_alive_interval:
                        await websocket.send(json.dumps({"type": "ping"}))
                        last_heartbeat = asyncio.get_event_loop().time()
                    
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=keep_alive_interval)
                        data = json.loads(message)
                        logger.info(f"Received data: {data}")
                        await process_data_func(data)
                    except asyncio.TimeoutError:
                        logger.warning("WebSocket connection timed out. Sending keep-alive ping.")
                        await websocket.send(json.dumps({"type": "ping"}))
                        last_heartbeat = asyncio.get_event_loop().time()
        except websockets.exceptions.ConnectionClosedError as e:  # Corrected exception
            logger.error(f"Connection to Pump.fun WebSocket closed with error: {e}. Reconnecting in {retry_interval} seconds...")
            await asyncio.sleep(retry_interval)
        except websockets.exceptions.ConnectionClosedOK as e:  # Corrected exception
            logger.error(f"Connection to Pump.fun WebSocket closed normally: {e}. Reconnecting in {retry_interval} seconds...")
            await asyncio.sleep(retry_interval)
        except websockets.exceptions.InvalidStatusCode as e:  # Corrected exception
            logger.error(f"WebSocket server rejected connection with status code: {e.status_code}")
            await asyncio.sleep(retry_interval)
        except Exception as e:
            logger.error(f"Unexpected error in Pump.fun WebSocket client: {str(e)}", exc_info=True)
            await asyncio.sleep(retry_interval)
        
        # Implement exponential backoff
        retry_interval = min(retry_interval * 2, 300)  # Cap at 300 seconds (5 minutes)

async def store_new_token_mint_data(data):
    logger.debug(f"Storing new token mint data: {data}")
    from backend.app import client  # Import the mongo instance
    from backend.models import Token  # Import the Token model

    # Create a new token instance with all required fields
    new_token = Token(
        contract_address=data.get('contract_address'),
        name=data.get('name', 'N/A'),
        symbol=data.get('symbol', 'N/A'),
        launch_date=data.get('launch_date', 'N/A'),
        price=data.get('price', 0)
    )

    if not new_token.contract_address:
        logger.error("Missing 'contract_address' key in data")
        return

    # Insert the new token into the database
    await client.db.tokens.insert_one(new_token.to_dict())

    # Further processing and inserting related data
    await fetch_and_store_token_metadata(new_token.contract_address)

from backend.app import client  # Import mongo instance
from backend.models import Trade, Token  # Import necessary models

async def fetch_and_store_token_metadata(contract_address):
    logger.debug(f"Fetching and storing token metadata for contract: {contract_address}")
    metadata = await (contract_address)
    token = client.db.tokens.find_one({"contract_address": contract_address})
    if token:
        update_data = {
            'name': metadata.get('name', 'N/A'),
            'symbol': metadata.get('symbol', 'N/A'),
            'launch_date': metadata.get('launch_date', 'N/A'),
            'price': metadata.get('price', 0),
            'volume': metadata.get('volume', 0)
        }
        client.db.tokens.update_one({'_id': token['_id']}, {'$set': update_data})
    else:
        new_token = Token(
            name=metadata.get('name', 'N/A'),
            symbol=metadata.get('symbol', 'N/A'),
            launch_date=metadata.get('launch_date', 'N/A'),
            price=metadata.get('price', 0),
            volume=metadata.get('volume', 0),
            contract_address=contract_address
        )
        client.db.tokens.insert_one(new_token.to_dict())

    # Further processing and inserting related data
    await store_token_data(metadata)

async def store_trade_data(data):
    logger.debug(f"Storing trade data: {data}")
    new_trade = Trade(
        token=data['token'],
        trade_time=data['trade_time'],
        amount=data['amount'],
        price=data['price']
    )
    client.db.trades.insert_one(new_trade.to_dict())

    # Further processing and inserting related data
    await process_data(data)

async def process_data(data):
    logger.debug(f"Processing data: {data}")
    try:
        if data.get('txType') == 'create':
            await store_new_token_mint_data(data)
        elif data.get('event') == 'trade':
            await store_trade_data(data)
        elif data.get('event') == 'mevBotTransaction':
            from backend.mev_bot import MEVBot
            from solana.rpc.api import Client as SolanaClient
            from bitquery import BitqueryClient  # Corrected import

            solana_client = SolanaClient("https://api.mainnet-beta.solana.com")  # Provide the Solana RPC URL
            bitquery_client = BitqueryClient(api_key=os.getenv("BITQUERY_API_KEY"))  # Initialize Bitquery client with API key
            mev_bot = MEVBot(solana_client, bitquery_client)
            await mev_bot.execute_transaction(data)

except websockets.ConnectionClosedError:
    logger.error("Connection to Pump.fun WebSocket closed. Reconnecting...")
    await asyncio.sleep(5)
except websockets.ConnectionClosedOK:
    logger.error("Connection to Pump.fun WebSocket closed normally. Reconnecting...")
    await asyncio.sleep(5)
except Exception as e:
    logger.error(f"Error in Pump.fun WebSocket client: {str(e)}", exc_info=True)
    await asyncio.sleep(5)
finally:
    if data.get('txType') == 'create':
        mint = data.get('mint')
        trader_public_key = data.get('traderPublicKey')
        initial_buy = data.get('initialBuy')
        bonding_curve_key = data.get('bondingCurveKey')
        v_tokens_in_bonding_curve = data.get('vTokensInBondingCurve')
        v_sol_in_bonding_curve = data.get('vSolInBondingCurve')
        market_cap_sol = data.get('marketCapSol')
        logger.info(f"New token mint data: {mint}, {trader_public_key}, {initial_buy}, {bonding_curve_key}, {v_tokens_in_bonding_curve}, {v_sol_in_bonding_curve}, {market_cap_sol}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(pump_fun_client("wss://pumpportal.fun/api/data", "subscribeNewToken", process_data))
    except KeyboardInterrupt:
        logger.info("WebSocket client stopped by user")
    finally:
        loop.close()
