import pytest
from websocket import create_connection

def test_pumpfun_integration():
    # Test WebSocket connection for Pump.fun integration
    ws = create_connection("ws://pumpportal.fun/ws/data")
    assert ws.connected, "WebSocket connection failed"
    ws.close()
