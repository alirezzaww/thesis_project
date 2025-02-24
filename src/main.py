import sys
import os
import time
from multiprocessing import Pool
import rsa
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
successful_tx = 0

def process_transaction(tx):
    tx_start = time.time()
    pre_prepared_msg = consensus.pre_prepare(tx)
    prepared_msg = consensus.prepare(pre_prepared_msg)
    if consensus.commit(prepared_msg):
        blockchain.add_block([tx])
        global successful_tx
        successful_tx += 1
    tx_end = time.time()
    print(f"Latency for {tx}: {tx_end - tx_start:.6f} seconds")

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        pool.map(process_transaction, transactions)

end_time = time.time()
total_time = end_time - start_time
tps = successful_tx / total_time if total_time > 0 else 0
print(f"\n[Performance] TPS: {tps:.2f}, Total Execution Time: {total_time:.2f} seconds")

# Print the current state of the blockchain
print("\n[DAG Blockchain Structure]")
for block in blockchain.blocks:
    print(f"Block {block.index} | Hash: {block.hash} | Parents: {block.previous_hashes}")
