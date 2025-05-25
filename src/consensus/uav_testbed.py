import random
import time
from consensus.hybrid_consensus import UPBFT
from consensus.dag_blockchain import DAGBlockchain

class UAVTestbed:
    def __init__(self, num_uavs):
        self.uavs = [f"UAV_{i}" for i in range(1, num_uavs + 1)]
        self.consensus = UPBFT(self.uavs, f=1)
        self.blockchain = DAGBlockchain(self.consensus)

    def simulate_network(self, num_rounds=5000):
        """Simulate UAV blockchain transaction processing."""
        start_time = time.time()
        for _ in range(num_rounds):
            leader = self.consensus.elect_leader()
            self.blockchain.add_block(["Tx"], leader)
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n=== Simulation Summary ===")
        print(f"Rounds: {num_rounds}, Duration: {duration:.2f}s")
        print("Consensus metrics:", self.consensus.performance_metrics)
        # Print DAG metrics if available
        try:
            dag_metrics = self.blockchain.get_performance_metrics()
            print("DAG metrics:", dag_metrics)
        except AttributeError:
            pass
