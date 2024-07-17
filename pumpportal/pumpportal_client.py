import asyncio
import requests
import os
from dotenv import load_dotenv
from service.App import App
from database.models import Token, TokenMetadata
from database.database import SessionLocal
import aiohttp
from backend.websocket_client import pump_fun_client, process_data

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
        db = SessionLocal()
        try:
            token = Token(
                contract_address=event["event"]["contractAddress"],
                creation_time=event["event"]["timestamp"]
            )
            db.add(token)
            db.commit()

            token_metadata = TokenMetadata(
                token_id=token.id,
                name=metadata.get("name"),
                symbol=metadata.get("symbol"),
                decimals=metadata.get("decimals"),
                total_supply=metadata.get("totalSupply")
            )
            db.add(token_metadata)
            db.commit()

            # Store trade details if available
            if "trades" in event:
                for trade in event["trades"]:
                    trade_record = Trade(
                        token_id=token.id,
                        trade_time=trade["timestamp"],
                        amount=trade["amount"],
                        price=trade["price"]
                    )
                    db.add(trade_record)
                db.commit()
        finally:
            db.close()

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
