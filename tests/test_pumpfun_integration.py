import pytest
import requests

def test_pumpfun_integration():
    # Test endpoint for Pump.fun integration
    response = requests.get("https://pumpportal.fun/api/data")
    assert response.status_code == 200
    assert "data" in response.json()
