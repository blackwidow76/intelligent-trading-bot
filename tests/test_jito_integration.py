import pytest
import requests

def test_jito_integration():
    # Test endpoint for Jito integration
    response = requests.get("https://ny.mainnet.block-engine.jito.wtf/")
    assert response.status_code == 200
    assert "result" in response.json()
