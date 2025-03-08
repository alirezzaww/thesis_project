import time
from consensus.hybrid_consensus import UPBFT
from consensus.dag_blockchain import DAGBlockchain
from consensus.trust_model import TrustModel

# Initialize Trust Model
trust_model = TrustModel(nodes=["Node1", "Node2", "Node3", "Node4"])

# Initialize Consensus with Trust Model
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1, trust_model=trust_model)

# Initialize Blockchain
blockchain = DAGBlockchain(consensus=consensus)

# Detect Byzantine nodes before transactions
consensus.detect_malicious_nodes()

# Optimize node selection
selected_nodes = consensus.trust_model.optimize_node_selection()

# Example Transactions
NUM_TRANSACTIONS = 10000
BATCH_SIZE = 500
transactions = [f"Tx{i}" for i in range(1, NUM_TRANSACTIONS + 1)]

def process_transaction_batch(batch):
    proposer_node = consensus.elect_leader(rounds=3)
    if proposer_node is None:
        print("[ERROR] ❌ No valid proposer found. Skipping batch.")
        return

    for tx in batch:
        pre_prepared_msg = consensus.pre_prepare(tx)
        prepared_msg = consensus.prepare(pre_prepared_msg)
        if consensus.commit(prepared_msg):
            blockchain.add_block([tx], proposer_node)

if __name__ == "__main__":
    start_time = time.perf_counter()
    for i in range(0, len(transactions), BATCH_SIZE):
        batch = transactions[i:i + BATCH_SIZE]
        process_transaction_batch(batch)
    execution_time = max(time.perf_counter() - start_time, 0.1)
    blockchain.validate_dag()
