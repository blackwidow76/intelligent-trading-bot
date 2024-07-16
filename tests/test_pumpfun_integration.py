import pytest
from backend.websocket_client import pump_fun_client

def test_pumpfun_integration():
    # Test WebSocket connection for Pump.fun integration
    ws = pump_fun_client(   )
    assert ws.connected, "WebSocket connection failed"
    ws.close()
