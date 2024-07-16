from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import asyncio

class SolanaClient:
    def __init__(self, rpc_url):
        self.client = AsyncClient(rpc_url, commitment=Confirmed)

    async def get_balance(self, public_key):
        response = await self.client.is_connected()
        if response:
            balance = await self.client.get_balance(public_key)
            return balance['result']['value'] / 10**9  # Convert lamports to SOL
        else:
            raise ConnectionError("Failed to connect to Solana network")

    async def get_recent_blockhash(self):
        return await self.client.get_recent_blockhash()

    # Add more Solana-specific methods here

    async def close(self):
        await self.client.close()
