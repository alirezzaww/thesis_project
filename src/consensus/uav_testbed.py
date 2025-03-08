import random
import time
from consensus.hybrid_consensus import UPBFT
from consensus.dag_blockchain import DAGBlockchain

class UAVTestbed:
    def __init__(self, num_uavs):
        self.uavs = [f"UAV_{i}" for i in range(1, num_uavs + 1)]
        self.consensus = UPBFT(self.uavs, f=1)
        self.blockchain = DAGBlockchain(self.consensus)

    def simulate_network(self):
        """Simulate UAV blockchain transaction processing."""
        for _ in range(5000):
            leader = self.consensus.elect_leader()
            self.blockchain.add_block(["Tx"], leader)
