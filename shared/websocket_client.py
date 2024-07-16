import asyncio
import websockets.client

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def __aenter__(self):
        self.websocket = await websockets.client.connect(self.uri)
        return self.websocket

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.websocket.close()
