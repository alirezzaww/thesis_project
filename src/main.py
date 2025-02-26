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
NUM_TRANSACTIONS = 5000  # Large-scale test
BATCH_SIZE = 100  # Efficient batching
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]


def process_transaction_batch(batch):
    """
    Processes a batch of transactions by running the consensus process
    and adding validated transactions to the DAG Blockchain.
    """
    consensus.elect_leader()  # Leader selection before processing

    for tx in batch:
        tx_start_time = time.time()  # Capture start time

        # Run the consensus steps
        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)
        
        if consensus.commit(prepared_msg):
            new_block = blockchain.add_block([tx])  # Corrected function call
            if new_block:
                print(f"[INFO] Transaction {tx} added successfully.")
            else:
                print(f"[ERROR] Transaction {tx} failed to be added.")

        tx_end_time = time.time()  # Capture end time
        latency = tx_end_time - tx_start_time  # Compute latency
        print(f"Latency for {tx}: {latency:.6f} seconds")


if __name__ == "__main__":
    start_time = time.perf_counter()  # More accurate than time.time()
    pool = multiprocessing.Pool(processes=4)

    # Process transactions in batches
    try:
        for i in range(0, len(transactions), BATCH_SIZE):
            batch = transactions[i:i + BATCH_SIZE]
            pool.apply_async(process_transaction_batch, (batch,))

        pool.close()
        pool.join()

    except Exception as e:
        print(f"[ERROR] Transaction Pooling Failed: {e}")

    execution_time = time.perf_counter() - start_time

    # Validate DAG structure after execution
    blockchain.validate_dag()

    # Print performance metrics
    TPS = len(transactions) / execution_time if execution_time > 0 else 0
    print(f"\n[Performance] TPS: {TPS:.2f}, Total Execution Time: {execution_time:.2f} seconds")

    # Simulate Byzantine failures for security testing
    consensus.simulate_byzantine_failures()

    # Visualize DAG structure
    blockchain.visualize_dag()
