import time
from .hybrid_consensus import UPBFT
from .dag_blockchain import DAGBlockchain
from .trust_model import TrustModel

# Initialize Trust Model
trust_model = TrustModel(nodes=["Node1", "Node2", "Node3", "Node4"])

# Initialize Consensus with Trust Model
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1, trust_model=trust_model)

# Initialize Blockchain
blockchain = DAGBlockchain(consensus=consensus)

def benchmark():
    """Measures Transactions Per Second (TPS) and Execution Time"""
    start_time = time.perf_counter()
    
    for _ in range(10000):
        leader = consensus.elect_leader()
        blockchain.add_block(["Tx"], leader)
    
    execution_time = max(time.perf_counter() - start_time, 0.1)
    TPS = len(blockchain.blocks) / execution_time
    
    print(f"[Performance] 📊 TPS: {TPS:.2f}, Total Execution Time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    benchmark()
