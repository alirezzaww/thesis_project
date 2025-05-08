import json
import sys
import time
from flask import Flask, request, jsonify
import joblib
import numpy as np
from web3 import Web3

# Add src to Python path
sys.path.append('./src')

from src.consensus.hybrid_consensus import UPBFT
from src.consensus.dag_blockchain import DAGBlockchain
from src.consensus.trust_model import TrustModel

app = Flask(__name__)

# Load AI fraud detection model
model = joblib.load("fraud_detection_model.pkl")

# Initialize Blockchain Consensus Layer
trust_model = TrustModel(nodes=["Node1", "Node2", "Node3", "Node4"])
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1, trust_model=trust_model)
blockchain = DAGBlockchain(consensus=consensus)

# Connect to Local Hardhat Blockchain
web3 = Web3(Web3.HTTPProvider("http://hardhat-node:8545"))

# Load Smart Contract
contract_address = Web3.to_checksum_address("0x5fbdb2315678afecb367f032d93f642f64180aa3")
with open("artifacts/contracts/EnhancedConsensus.sol/EnhancedConsensus.json", "r") as f:
    contract_json = json.load(f)
    contract_abi = contract_json["abi"]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Initialize web3 connection early
for attempt in range(10):
    try:
        accounts = web3.eth.accounts
        web3.eth.default_account = accounts[0]
        print(f"[INFO] ✅ Connected to Hardhat. Using account {accounts[0]}")
        break
    except Exception as e:
        print(f"[WAITING] ⏳ Waiting for Hardhat node... Attempt {attempt + 1}/10")
        time.sleep(2)
else:
    raise ConnectionError("❌ Failed to connect to Hardhat node after 10 attempts.")

# ---------------------- ROUTES ----------------------

@app.route('/predict', methods=['POST'])
def predict_fraud():
    data = request.json
    features = np.array([[
        data['amount'],
        data['transaction_time'],
        data['num_transactions_past_week'],
        data['sender_encoded'],
        data['receiver_encoded']
    ]])
    prediction = model.predict(features)[0]

    if prediction == 1:
        tx_hash = contract.functions.flagFraudulent(data['transaction_id']).transact()
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"message": "🚨 Fraud detected!", "transaction_id": data['transaction_id']})
    else:
        proposer = consensus.elect_leader(blockchain)
        if proposer is None:
            return jsonify({
                "error": "❌ No eligible proposer found. Try again later or verify trust scores."
            }), 500

        blockchain.add_block([data['transaction_id']], proposer)
        return jsonify({
            "message": "✅ Transaction is safe & added to DAG.",
            "transaction_id": data['transaction_id'],
            "proposer": proposer
        })

@app.route('/add_tx', methods=['POST'])
def add_transaction():
    data = request.json
    tx_hash = contract.functions.addTransaction(
        data['receiver'],
        int(data['amount']),
        data.get('parentTxs', [])
    ).transact()
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"message": "Transaction submitted.", "tx_hash": receipt.transactionHash.hex()})

@app.route('/approve_tx', methods=['POST'])
def approve_transaction():
    data = request.json
    tx_hash = contract.functions.approveTransaction(data['transaction_id']).transact()
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"message": "Transaction approved.", "tx_hash": receipt.transactionHash.hex()})

@app.route('/update_energy', methods=['POST'])
def update_energy():
    data = request.json
    tx_hash = contract.functions.updateEnergyScore(data['validator'], data['score']).transact()
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"message": "Energy score updated.", "tx_hash": receipt.transactionHash.hex()})

@app.route('/rotate_leader', methods=['POST'])
def rotate_leader():
    tx_hash = contract.functions.rotateLeader().transact()
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({"message": "Leader rotated.", "tx_hash": receipt.transactionHash.hex()})

@app.route('/get_leader', methods=['GET'])
def get_leader():
    leader = contract.functions.getCurrentLeader().call()
    return jsonify({"leader": leader})

@app.route('/validators', methods=['GET'])
def get_validators():
    val_list = contract.functions.getAllValidators().call()
    return jsonify({"validators": val_list})

@app.route('/get_blocks', methods=['GET'])
def get_blocks():
    blocks = [{"index": block.index, "transactions": block.transactions, "proposer": block.proposer} for block in blockchain.blocks]
    return jsonify({"blocks": blocks})

@app.route('/validate_dag', methods=['GET'])
def validate_dag():
    is_valid = blockchain.validate_dag()
    return jsonify({"dag_valid": is_valid})

@app.route('/trust_scores', methods=['GET'])
def get_trust_scores():
    return jsonify({"trust_scores": trust_model.trust_scores})

@app.route('/malicious_nodes', methods=['GET'])
def get_malicious_nodes():
    return jsonify({"malicious_nodes": list(consensus.malicious_nodes)})

@app.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    data = request.json
    attacker = data.get("attacker", "Node1")
    fake_tx = f"FakeTx-{attacker}"
    blockchain.add_block([fake_tx], attacker)
    return jsonify({"message": "⚠️ Simulated malicious transaction submitted.", "attacker": attacker})

# ---------------------- RUN ----------------------

# Root endpoint to show API is running
@app.route('/')
def index():
    return jsonify({"message": "🚀 Thesis API is up and running!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
