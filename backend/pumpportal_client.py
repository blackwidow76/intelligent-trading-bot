import asyncio
import requests
import os
from dotenv import load_dotenv
from service.App import App
from database.models import Token
import aiohttp
from .websocket_client import pump_fun_client, process_data
from pymongo import MongoClient

client = MongoClient(App.config["MONGODB_URI"])
db = client.get_database('pumpportal')  # Replace 'your_database_name' with the actual database name

async def fetch_token_metadata(contract_address):
    url = f"https://pumpportal.fun/api/data/token-info?ca={contract_address}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to fetch metadata for {contract_address}")

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

    async def fetch_token_metadata(self, token_metadata_url):
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
                # Add other token fields here
            }
            tokens_collection.insert_one(token_document)
            # Further processing and inserting related data
        except Exception as e:
            print(f"An error occurred: {e}")

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