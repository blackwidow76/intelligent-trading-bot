import asyncio
import websockets
import json
import requests
import os
from dotenv import load_dotenv
from service.App import App
from database.models import Token, TokenMetadata
from database.database import SessionLocal

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
        async with websockets.connect(self.websocket_url) as websocket:
            payload = {
                "method": "subscribeNewToken",
            }
            await websocket.send(json.dumps(payload))
            async for message in websocket:
                event = json.loads(message)
                if event.get("event") == "newToken":
                    token_metadata = await self.get_token_metadata(event["contractAddress"])
                    await self.store_token_data(event, token_metadata)
                    yield {"event": event, "metadata": token_metadata}

    async def get_token_metadata(self, contract_address):
        response = requests.get(f"{self.token_metadata_url}/{contract_address}")
        return response.json()

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
        finally:
            db.close()

    async def subscribe_account_trade(self, accounts):
        async with websockets.connect(self.websocket_url) as websocket:
            payload = {
                "method": "subscribeAccountTrade",
                "keys": accounts
            }
            await websocket.send(json.dumps(payload))
            async for message in websocket:
                yield json.loads(message)

    async def subscribe_token_trade(self, tokens):
        async with websockets.connect(self.websocket_url) as websocket:
            payload = {
                "method": "subscribeTokenTrade",
                "keys": tokens
            }
            await websocket.send(json.dumps(payload))
            async for message in websocket:
                yield json.loads(message)

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
