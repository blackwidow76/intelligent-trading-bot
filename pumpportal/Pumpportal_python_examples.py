#Real-time Updates
#Stream real-time trading and token creation data by connecting to the PumpPortal Websocket at wss://pumpportal.fun/api/data.

#Once you connect, you can subscribe to different data streams. The following methods are available:

#subscribeNewToken For token creation events.

#subscribeTokenTrade For all trades made on specific token(s).

#subscribeAccountTrade For all trades made by specific account(s).

#PLEASE ONLY USE ONE WEBSOCKET CONNECTION AT A TIME:
#You should NOT open a new Websocket connection for every token or account you subscribe to. Instead, you should send any new subscribe messages to the same connection. Clients that repeatedly attempt to open many websocket connections at once may be blacklisted. If this happens you must reach out in Telegram so we can remove the ban.

#Examples:
"""
Python
JavaScript
import asyncio
import websockets
import json

async def subscribe():
uri = "wss://pumpportal.fun/api/data"
async with websockets.connect(uri) as websocket:
    
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
        print(json.loads(message))

# Run the subscribe function
asyncio.get_event_loop().run_until_complete(subscribe())
"""


#You can also unsubscribe from any data stream in the same way, using the following methods:

#unsubscribeNewToken

#unsubscribeTokenTrade

#unsubscribeAccountTrade

#Python
import asyncio
import websockets
import json

async def subscribe():
uri = "wss://pumpportal.fun/api/data"
async with websockets.connect(uri) as websocket:
    
    # Subscribing to token creation events
    payload = {
        "method": "subscribeNewToken",
    }
    await websocket.send(json.dumps(payload))
    
    # Unsubscribing from new token events
    payload = {
        "method": "unsubscribeNewToken",
    }
    await websocket.send(json.dumps(payload))
    
    async for message in websocket:
        print(json.loads(message))

# Run the subscribe function
asyncio.get_event_loop().run_until_complete(subscribe())
