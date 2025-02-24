import hashlib
import time
import random
import numpy as np
from collections import defaultdict

# Define a Block in the DAG
class Block:
    def __init__(self, index, previous_hashes, transactions, timestamp=None):
        self.index = index
        self.previous_hashes = previous_hashes  # Multiple parents (DAG structure)
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_data = f"{self.index}{self.previous_hashes}{self.transactions}{self.timestamp}"
        return hashlib.sha256(block_data.encode()).hexdigest()

# DAG-based Blockchain
class DAGBlockchain:
    def __init__(self):
        self.blocks = []
        self.graph = defaultdict(list)  # DAG adjacency list
        self.genesis_block()

    def genesis_block(self):
        genesis = Block(0, [], ["Genesis Block"])
        self.blocks.append(genesis)
        self.graph[genesis.hash] = []

    def add_block(self, transactions):
        parent_hashes = self.get_parent_blocks()
        new_block = Block(len(self.blocks), parent_hashes, transactions)
        self.blocks.append(new_block)
        for parent in parent_hashes:
            self.graph[parent].append(new_block.hash)
        self.graph[new_block.hash] = []
        return new_block

    def get_parent_blocks(self):
        if len(self.blocks) < 2:
            return [self.blocks[-1].hash]
        return [block.hash for block in self.blocks[-2:]]

# U-PBFT (Hierarchical Byzantine Fault Tolerance for UAVs)
class UPBFT:
    def __init__(self, nodes, f):
        self.nodes = nodes
        self.f = f  # Max Byzantine nodes tolerated
        self.leader = None
        self.state = {}
        self.malicious_nodes = set()
        self.node_scores = {node: np.random.uniform(0, 1) for node in self.nodes}  # AI-based ranking

    def elect_leader(self):
        """Choose the node with the highest efficiency score as the leader."""
        self.leader = max(self.node_scores, key=self.node_scores.get)
        print(f"[LEADER ELECTION] AI-Selected Leader: {self.leader}")

    def simulate_malicious_nodes(self, probability=0.2):
        """Randomly mark some nodes as malicious with a given probability."""
        for node in self.nodes:
            if random.random() < probability:
                self.malicious_nodes.add(node)
        print(f"[SECURITY] Malicious nodes detected: {self.malicious_nodes}")

    def optimize_node_selection(self):
        """Select a subset of high-efficiency nodes for consensus."""
        sorted_nodes = sorted(self.node_scores.items(), key=lambda x: x[1], reverse=True)
        selected_nodes = [node for node, score in sorted_nodes[:len(self.nodes)//2]]
        return selected_nodes

    def pre_prepare(self, transaction):
        if self.leader is None:
            self.elect_leader()
        return {node: transaction for node in self.nodes if node not in self.malicious_nodes}

    def prepare(self, message):
        confirmations = {node: message for node in self.nodes if node not in self.malicious_nodes}
        return confirmations

    def commit(self, confirmations):
        valid_votes = len(confirmations) - len(self.malicious_nodes)
        if valid_votes >= 2 * self.f + 1:
            print("[COMMIT] Transaction committed.")
            return True
        print("[COMMIT] Transaction failed due to Byzantine nodes.")
        return False
