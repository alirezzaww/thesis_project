import json
from flask import Flask, request, jsonify
import joblib
import numpy as np
from web3 import Web3
from consensus.hybrid_consensus import UPBFT
from consensus.dag_blockchain import DAGBlockchain
from consensus.trust_model import TrustModel

app = Flask(__name__)

# Load AI model
model = joblib.load("fraud_detection_model.pkl")

# Initialize Blockchain Consensus
trust_model = TrustModel(nodes=["Node1", "Node2", "Node3", "Node4"])
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1, trust_model=trust_model)
blockchain = DAGBlockchain(consensus=consensus)

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
    """Analyze transaction for fraud & submit to blockchain if safe."""
    data = request.json
    features = np.array([[data['amount'], data['transaction_time'], data['num_transactions_past_week'], data['sender_encoded'], data['receiver_encoded']]])
    prediction = model.predict(features)[0]

    if prediction == 1:
        tx_hash = contract.functions.flagTransaction(data['transaction_id']).transact()
        web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"message": "🚨 Fraud detected!", "transaction_id": data['transaction_id']})
    else:
        # Submit transaction to DAG Blockchain Consensus
        proposer = consensus.elect_leader()
        blockchain.add_block([data['transaction_id']], proposer)

        return jsonify({
            "message": "✅ Transaction is safe & added to blockchain.",
            "transaction_id": data['transaction_id'],
            "proposer": proposer
        })

@app.route('/get_blocks', methods=['GET'])
def get_blocks():
    """Retrieve all blocks from DAG blockchain."""
    blocks = [{"index": block.index, "transactions": block.transactions, "proposer": block.proposer} for block in blockchain.blocks]
    return jsonify({"blocks": blocks})

@app.route('/get_leader', methods=['GET'])
def get_leader():
    """Get the current leader from consensus."""
    leader = consensus.elect_leader()
    return jsonify({"leader": leader})

@app.route('/validate_dag', methods=['GET'])
def validate_dag():
    """Check DAG blockchain validity."""
    is_valid = blockchain.validate_dag()
    return jsonify({"dag_valid": is_valid})

if __name__ == '__main__':
    app.run(debug=True)
