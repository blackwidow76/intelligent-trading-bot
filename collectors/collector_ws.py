import os
import sys
import argparse
import asyncio
import websockets  # Ensure you have the latest version of websockets installed
import json
import logging
from typing import Optional  # Add this import if not already present

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Add the grandparent directory to the Python path
path_to_add = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
print(f"Adding path: {path_to_add}")  # Added print statement to debug path modification
sys.path.insert(0, path_to_add)

from service.App import App
from service.analyzer import Analyzer
# Subscribe to a stream and receive the events with updates
# The received data is stored in the corresponding files
#

async def subscribe_to_streams(websocket, streams):
    for stream in streams:
        payload = {
            "method": "subscribe",
            "stream": stream
        }
        await websocket.send(json.dumps(payload))

# Call the function within an async context
async def main():   
    uri = "wss://pumpportal.fun/api/data"  # Replace with actual URI
    async with websockets.connect(uri) as websocket:  # Correct usage of websockets.connect
        await subscribe_to_streams(websocket, ["stream1", "stream2"])  # Example streams
        async for message in websocket:
            data = json.loads(message)
            log.info(f"Received data: {data}")
#  Create event queue for processing incoming events. Writings to one file must be sequential - not in parallel.
#    But writes in different files can be independent tasks.
#    How to ensure sequential tasks? Essentially, incoming events are not allowed to overlap somewhere down the pipeline (at the end).
#  Store two streams (klines and depth) for all listed symbols in test files
#  Check for:
#   - recover after lost/bad connection (errors)
#   - continuation of connection (confirmation responses) - chect if it is done automatically by the client


async def process_data(msg):
    if msg is None:
        log.error("Empty message received")
        return
    if not isinstance(msg, dict):
        log.error("Message received is not dict")
        return

    event = msg.get('data')
    if event is None:
        log.error("Empty event received")
        return

    event_type = event.get('event')
    if event_type == 'error':
        log.error("Event error")
        return

    log.info(f"Event received: {event}")

    # Store the received data using Bitquery API
    await store_data_with_bitquery(event)

from database.database import db

def store_data(data):
    # Assuming 'data' collection exists in the database
    db.data.insert_one(data)


def start_collector_ws():
    print(f"Start collecting data using WebSocket streams.")

    #
    # Initialize data state, connections and listeners
    #
    App.analyzer = Analyzer(None)  # This should now be compatible with the type hint

    #
    # Register websocket listener
    #

    # List of streams
    channels = App.config["collector"]["stream"]["channels"]
    print(f"Channels: {channels}")

    # List of symbols
    symbols = App.config["collector"]["stream"]["symbols"]
    print(f"Channels: {symbols}")

    streams = []
    for c in channels:
        for s in symbols:
            stream = s.lower() + "@" + c.lower()
            streams.append(stream)
    print(f"Streams: {streams}")

    #
    # Start event loop
    #

    async def main():
        uri = "wss://pumpportal.fun/api/data"  # Replace with actual URI
        async with websockets.connect(uri) as websocket:  # Correct usage of websockets.connect
            await subscribe_to_streams(websocket, streams)
            async for message in websocket:
                data = json.loads(message)
                process_message(data)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    print(f"End collecting data using WebSocket streams.")

    return 0


if __name__ == "__main__":
    start_collector_ws()

    pass
