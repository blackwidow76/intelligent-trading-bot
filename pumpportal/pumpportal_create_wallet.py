# PumpPortal Create Wallet

import requests
 
response = requests.get(url="https://pumpportal.fun/api/create-wallet")
 
# JSON with keys for a newly generated wallet and the linked API key
data = response.json()

print(data)
