import json
from web3 import Web3
import joblib
import numpy as np

# Connect to Hardhat blockchain
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Load ABI from compiled contract JSON
with open("artifacts/contracts/TransactionStorage.sol/TransactionStorage.json", "r") as f:
    contract_json = json.load(f)
    contract_abi = contract_json["abi"]  # ✅ Correct way to load ABI

# Smart contract details
contract_address = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"  # Replace with actual deployed address

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Load trained fraud detection model
model = joblib.load("fraud_detection_model.pkl")

# Simulate a transaction
transaction_id = 4
sender = "0x123"
receiver = "0x456"
amount = 10000
transaction_time = 45000
num_transactions_past_week = 5
sender_encoded = 3
receiver_encoded = 7

# Prepare data for model prediction
features = np.array([[amount, transaction_time, num_transactions_past_week, sender_encoded, receiver_encoded]])
prediction = model.predict(features)[0]

if prediction == 1:
    print("🚨 Fraud Detected! Flagging transaction on Blockchain.")
    tx_hash = contract.functions.flagTransaction(transaction_id).transact()
    web3.eth.wait_for_transaction_receipt(tx_hash)
else:
    print("✅ Transaction is safe.")
