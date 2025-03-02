import time
from consensus.hybrid_consensus import DAGBlockchain, UPBFT

# 1. Initialize Consensus
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)

# 2. Detect Byzantine nodes before transactions
consensus.detect_malicious_nodes()

# 3. Optimize node selection based on AI-based scoring
selected_nodes = consensus.optimize_node_selection()

# 4. Initialize Blockchain, passing the same consensus object
blockchain = DAGBlockchain(consensus=consensus)

# 5. Example Transactions
NUM_TRANSACTIONS = 10000
BATCH_SIZE = 500
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]

def process_transaction_batch(batch):
    """
    Process a batch of transactions with leader election and consensus rounds.
    We run in a single process (no multiprocessing), so the main DAG is updated
    directly here.
    """
    proposer_node = consensus.elect_leader(rounds=3)  # Keep the same leader for 3 consecutive batches

    if proposer_node is None:
        print("[ERROR] ❌ No valid proposer found. Skipping batch.")
        return

    print(f"[INFO] 🚀 Processing batch by leader {proposer_node}")

    for tx in batch:
        tx_start_time = time.time()

        # PBFT steps
        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)

        if consensus.commit(prepared_msg):
            # Add a block containing this transaction
            new_block = blockchain.add_block([tx], proposer_node)
            if new_block:
                print(f"[BLOCK ADDED] ✅ Block {new_block.index} added by {proposer_node}.")
            else:
                print(f"[WARNING] ❌ Block NOT added for transaction {tx}.")

        tx_end_time = time.time()
        latency = tx_end_time - tx_start_time
        print(f"[INFO] ⏳ Latency for {tx}: {latency:.6f} seconds")

    print(f"[INFO] ✅ Batch completed by Leader: {proposer_node}")

if __name__ == "__main__":
    start_time = time.perf_counter()  # More accurate timing

    # 6. Process transactions in a single loop (no multiprocessing)
    for i in range(0, len(transactions), BATCH_SIZE):
        batch = transactions[i:i + BATCH_SIZE]
        process_transaction_batch(batch)

    # 7. Measure execution time
    execution_time = max(time.perf_counter() - start_time, 0.1)

    # 8. Validate DAG structure after execution
    blockchain.validate_dag()

    # 9. Calculate TPS based on confirmed transactions in the DAG
    confirmed_tx = sum(len(block.transactions) for block in blockchain.blocks)
    TPS = confirmed_tx / execution_time if execution_time > 0 else 0
    print(f"\n[Performance] 📊 TPS: {TPS:.2f}, Total Execution Time: {execution_time:.2f} seconds")

    # 10. Simulate Byzantine failures for security testing
    consensus.simulate_byzantine_failures()

    # 11. Visualize only the last 50 blocks of the DAG (for readability)
    blockchain.visualize_dag(malicious_nodes=consensus.malicious_nodes, num_blocks=50)
