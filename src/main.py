import time
import multiprocessing
from consensus.hybrid_consensus import DAGBlockchain, UPBFT

# Initialize Blockchain and Consensus
blockchain = DAGBlockchain()
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)

# Detect Byzantine nodes before transactions
consensus.detect_malicious_nodes()

# Optimize node selection based on AI-based scoring
selected_nodes = consensus.optimize_node_selection()

# Example Transactions
NUM_TRANSACTIONS = 10000  # Scale up for large tests
BATCH_SIZE = 500  # Larger batch size for efficiency
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]


def process_transaction_batch(batch):
    """Process a batch of transactions with leader election and consensus rounds."""
    consensus.elect_leader()  # Select a proposer node
    proposer_node = consensus.leader  # Get the current leader

    for tx in batch:
        tx_start_time = time.time()

        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)

        if consensus.commit(prepared_msg):
            blockchain.add_block([tx], proposer_node)  # Pass proposer_node

        tx_end_time = time.time()
        latency = tx_end_time - tx_start_time
        print(f"Latency for {tx}: {latency:.6f} seconds")

    print(f"[INFO] Batch completed by Leader: {proposer_node}")


if __name__ == "__main__":
    start_time = time.perf_counter()  # More accurate than time.time()
    num_cores = multiprocessing.cpu_count()  # Detect available CPU cores
    num_workers = min(4, num_cores)  # Keep workers slightly higher for overlapping execution
    pool = multiprocessing.Pool(processes=num_workers)

    try:
        for i in range(0, len(transactions), BATCH_SIZE):
            batch = transactions[i:i + BATCH_SIZE]
            pool.apply_async(process_transaction_batch, (batch, start_time))

        pool.close()
        pool.join()

    except Exception as e:
        print(f"[ERROR] Transaction Pooling Failed: {e}")

    execution_time = max(time.perf_counter() - start_time, 0.01)  # Avoid division by near-zero


    # Validate DAG structure after execution
    blockchain.validate_dag()

    TPS = len(transactions) / execution_time
    print(f"\n[Performance] TPS: {TPS:.2f}, Total Execution Time: {execution_time:.2f} seconds")

    # Simulate Byzantine failures for security testing
    consensus.simulate_byzantine_failures()

    # Visualize DAG structure
    blockchain.visualize_dag()
