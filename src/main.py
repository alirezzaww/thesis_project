import sys
import os
import time
from consensus.hybrid_consensus import DAGBlockchain, UPBFT

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialize Blockchain and Consensus Mechanism
blockchain = DAGBlockchain()
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)

# Simulate Byzantine node behavior and AI-based node selection
consensus.simulate_malicious_nodes(probability=0.2)
selected_nodes = consensus.optimize_node_selection()
print(f"[INFO] Optimized Node Selection: {selected_nodes}")

# Simulated Transactions with Performance Benchmarking
transactions = [f"Tx{i}" for i in range(1, 101)]  # Simulating 100 transactions

print("[Starting Hybrid Consensus Simulation]")
start_time = time.time()

for tx in transactions:
    print(f"\nProcessing Transaction: {tx}")
    pre_prepared_msg = consensus.pre_prepare(tx)
    prepared_msg = consensus.prepare(pre_prepared_msg)
    if consensus.commit(prepared_msg):
        blockchain.add_block([tx])
    else:
        print(f"[WARNING] Transaction {tx} failed consensus and was not added to the blockchain.")

end_time = time.time()
print(f"\n[Performance] Total Execution Time: {end_time - start_time:.2f} seconds")

# Print the current state of the blockchain
print("\n[DAG Blockchain Structure]")
for block in blockchain.blocks:
    print(f"Block {block.index} | Hash: {block.hash} | Parents: {block.previous_hashes}")
