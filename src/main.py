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
NUM_TRANSACTIONS = 5000  # Scale up for large tests
BATCH_SIZE = 100  # Larger batch size for efficiency
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]


def process_transaction_batch(batch, start_time):
    consensus.elect_leader()
    for tx in batch:
        tx_start_time = time.time()  # Capture time when transaction starts
    
    pre_prepared_msg = consensus.pre_prepare(tx)
    prepared_msg = consensus.prepare(pre_prepared_msg)

    if consensus.commit(prepared_msg):
        blockchain.add_block([tx], proposer_node)  # Include proposer node

    tx_end_time = time.time()  # Capture when transaction ends
    latency = tx_end_time - tx_start_time  # Ensure subtraction order is correct
    print(f"Latency for {tx}: {latency:.6f} seconds")


if __name__ == "__main__":
    start_time = time.time()
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

    execution_time = time.time() - start_time

    # Validate DAG structure after execution
    blockchain.validate_dag()

    # Print performance metrics
    print(f"\n[Performance] TPS: {len(transactions) / execution_time:.2f}, Total Execution Time: {execution_time:.2f} seconds")

    # Simulate Byzantine failures for security testing
    consensus.simulate_byzantine_failures()

    # Visualize DAG structure
    blockchain.visualize_dag()
