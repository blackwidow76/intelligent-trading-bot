import requests
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig

response = requests.post(url="https://pumpportal.fun/api/trade-local", data={
    "publicKey": "7o3WapwhoLJG2M1vwmsdocdwxnCSDJmCaGqVuCsooQkM",
    "action": "buy",             # "buy" or "sell"
    "mint": "<token CA here>",     # contract address of the token you want to trade
    "amount": 100000,            # amount of SOL or tokens to trade
    "denominatedInSol": "false", # "true" if amount is amount of SOL, "false" if amount is number of tokens
    "slippage": 10,              # percent slippage allowed
    "priorityFee": 0.005,        # amount to use as priority fee
    "pool": "pump"               # exchange to trade on. "pump" or "raydium"
})

keypair = Keypair.from_base58_string("Your base 58 private key here")
tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])

commitment = CommitmentLevel.Confirmed
config = RpcSendTransactionConfig(preflight_commitment=commitment)
txPayload = SendVersionedTransaction(tx, config)

response = requests.post(
    url="https://ny.mainnet.block-engine.jito.wtf/",
    headers={"Content-Type": "application/json"},
    data=SendVersionedTransaction(tx, config).to_json()
)
txSignature = response.json()['result']
print(f'Transaction: https://solscan.io/tx/{txSignature}')