import pytest
from backend.websocket_client import pump_fun_client, process_data

import asyncio

def test_pumpfun_integration():
    # Test WebSocket connection for Pump.fun integration
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ws = loop.run_until_complete(pump_fun_client(uri="wss://pumpportal.fun/api/data", method="subscribeNewToken", process_data_func=process_data))
    assert ws.connected, "WebSocket connection failed"
    ws.close()
