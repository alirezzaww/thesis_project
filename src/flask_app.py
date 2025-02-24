import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from consensus.hybrid_consensus import DAGBlockchain, UPBFT
import hashlib

app = Flask(__name__)

# Initialize Blockchain and Consensus Mechanism
blockchain = DAGBlockchain()
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)

@app.route("/submit_transaction", methods=["POST"])
def submit_transaction():
    data = request.json
    transaction = data.get("transaction")
    
    if not transaction:
        return jsonify({"error": "Transaction data is required"}), 400
    
    pre_prepared_msg = consensus.pre_prepare(transaction)
    prepared_msg = consensus.prepare(pre_prepared_msg)
    
    if consensus.commit(prepared_msg):
        block = blockchain.add_block([transaction])
        return jsonify({"message": "Transaction committed", "block_hash": block.hash}), 200
    else:
        return jsonify({"error": "Transaction failed consensus"}), 500

@app.route("/get_blockchain", methods=["GET"])
def get_blockchain():
    chain = [{
        "index": block.index,
        "hash": block.hash,
        "transactions": block.transactions,
        "parents": block.previous_hashes
    } for block in blockchain.blocks]
    return jsonify(chain), 200

@app.route("/get_transaction/<tx_hash>", methods=["GET"])
def get_transaction(tx_hash):
    for block in blockchain.blocks:
        for tx in block.transactions:
            if hashlib.sha256(tx.encode()).hexdigest() == tx_hash:
                return jsonify({"transaction": tx, "block_hash": block.hash}), 200
    return jsonify({"error": "Transaction not found"}), 404

@app.route("/get_dag_structure", methods=["GET"])
def get_dag_structure():
    return jsonify(blockchain.graph), 200

@app.route("/performance_metrics", methods=["GET"])
def performance_metrics():
    return jsonify(consensus.get_performance_metrics()), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

