import json  # ✅ Fix: Import JSON module
from flask import Flask, request, jsonify
import joblib
import numpy as np
from web3 import Web3

app = Flask(__name__)

# Load AI model
model = joblib.load("fraud_detection_model.pkl")

# Connect to blockchain
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
contract_address = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"

# Load ABI from compiled contract JSON
with open("artifacts/contracts/TransactionStorage.sol/TransactionStorage.json", "r") as f:
    contract_json = json.load(f)
    contract_abi = contract_json["abi"]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

@app.route('/predict', methods=['POST'])
def predict_fraud():
    data = request.json
    features = np.array([[data['amount'], data['transaction_time'], data['num_transactions_past_week'], data['sender_encoded'], data['receiver_encoded']]])
    prediction = model.predict(features)[0]

    if prediction == 1:
        tx_hash = contract.functions.flagTransaction(data['transaction_id']).transact()
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"message": "🚨 Fraud detected!", "transaction_id": data['transaction_id']})
    else:
        return jsonify({"message": "✅ Transaction is safe.", "transaction_id": data['transaction_id']})

if __name__ == '__main__':
    app.run(debug=True)
