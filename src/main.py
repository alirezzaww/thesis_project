import time
import multiprocessing
from consensus.hybrid_consensus import DAGBlockchain, UPBFT

# Initialize Blockchain and Consensus
blockchain = DAGBlockchain()
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1)
selected_nodes = consensus.optimize_node_selection()

# Example Transactions
NUM_TRANSACTIONS = 100
BATCH_SIZE = 10  # Process transactions in batches
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]

def process_transaction_batch(batch):
    consensus.elect_leader()
    for tx in batch:
        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)
        if consensus.commit(prepared_msg):
            blockchain.add_block([tx])
        latency = time.time() - start_time
        print(f"Latency for {tx}: {latency:.6f} seconds")

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

    print(f"\n[Performance] TPS: {len(transactions) / execution_time:.2f}, Total Execution Time: {execution_time:.2f} seconds")
    blockchain.visualize_dag()
