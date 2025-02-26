import time
import multiprocessing
from consensus.hybrid_consensus import DAGBlockchain, UPBFT

# Initialize Blockchain and Consensus
blockchain = DAGBlockchain()
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)

# Detect Byzantine nodes before transactions
consensus.detect_malicious_nodes()
selected_nodes = consensus.optimize_node_selection()

# Example Transactions
NUM_TRANSACTIONS = 5000  # Scale up for large tests
BATCH_SIZE = 100  # Larger batch size for efficiency
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]


def process_transaction_batch(batch):
    proposer_node = consensus.elect_leader()
    valid_transactions = []
    
    for tx in batch:
        tx_start_time = time.time()
        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)

        if consensus.commit(prepared_msg):
            valid_transactions.append(tx)
        
        tx_end_time = time.time()
        latency = tx_end_time - tx_start_time
        print(f"Latency for {tx}: {latency:.6f} seconds")
    
    # Add valid transactions as a block
    if valid_transactions:
        blockchain.add_block(valid_transactions, proposer_node)
    else:
        print("[WARNING] No valid transactions to add in this batch.")


if __name__ == "__main__":
    start_time = time.time()
    pool = multiprocessing.Pool(processes=4)

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
