import time
import multiprocessing
import json
from consensus.hybrid_consensus import DAGBlockchain, UPBFT

# Initialize Blockchain and Consensus
blockchain = DAGBlockchain()
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)
selected_nodes = consensus.optimize_node_selection()
consensus.detect_malicious_nodes()  # Detect any malicious nodes before starting

# Example Transactions
NUM_TRANSACTIONS = 100
BATCH_SIZE = 10  # Process transactions in batches
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]
consensus.simulate_byzantine_failures(failure_rate=0.3)
def process_transaction_batch(batch):
    """Processes a batch of transactions using U-PBFT consensus and DAG structure."""
    batch_start_time = time.time()
    
    consensus.elect_leader()
    for tx in batch:
        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)
        if consensus.commit(prepared_msg):
            blockchain.add_block([tx])
        
        latency = time.time() - batch_start_time
        print(f"Latency for {tx}: {latency:.6f} seconds")

def save_results_to_file(filename, tps, execution_time):
    """Save performance results to a JSON file for validation and analysis."""
    results = {
        "Total Transactions": len(transactions),
        "Total Time (s)": round(execution_time, 4),
        "TPS (Transactions Per Second)": round(tps, 4),
        "Average Latency (s)": round(execution_time / len(transactions), 6),
    }

    with open(filename, "w") as f:
        json.dump(results, f, indent=4)

    print(f"[INFO] Results saved to {filename}")

if __name__ == "__main__":
    start_time = time.time()
    pool = multiprocessing.Pool(processes=4)

    # Process transactions in batches
    for i in range(0, len(transactions), BATCH_SIZE):
        batch = transactions[i:i + BATCH_SIZE]
        pool.apply_async(process_transaction_batch, (batch,))

    pool.close()
    pool.join()
    execution_time = time.time() - start_time

def save_results_to_file(filename, tps, execution_time):
    """Save performance results to a JSON file for validation and analysis."""
    results = {
        "Total Transactions": len(transactions),
        "Total Time (s)": round(execution_time, 4),
        "TPS (Transactions Per Second)": round(tps, 4),
        "Average Latency (s)": round(execution_time / len(transactions), 6),
    }

    with open(filename, "w") as f:
        json.dump(results, f, indent=4)

    print(f"[INFO] Results saved to {filename}")

    # Print performance results
    performance_metrics = consensus.get_performance_metrics()
    print(f"\n[Performance] TPS: {performance_metrics['TPS (Transactions Per Second)']:.2f}, "
          f"Total Execution Time: {execution_time:.2f} seconds")
    print(f"Final Average Latency: {performance_metrics['Average Latency (s)']:.6f} seconds")

    # Detect Byzantine nodes
    consensus.detect_malicious_nodes()

    # Run DAG validation after execution
    if blockchain.validate_dag():
        print("[VALIDATION] DAG structure is correct!")

    blockchain.visualize_dag()
