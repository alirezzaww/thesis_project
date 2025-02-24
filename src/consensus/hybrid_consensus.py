import hashlib
import time
import random
import numpy as np
import rsa
from collections import defaultdict

# Generate RSA keys
(public_key, private_key) = rsa.newkeys(512)

# Define a Block in the DAG
class Block:
    def __init__(self, index, previous_hashes, transactions, timestamp=None):
        self.index = index
        self.previous_hashes = previous_hashes  # Multiple parents (DAG structure)
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.hash = self.compute_hash()
        self.signature = self.sign_block()

    def compute_hash(self):
        block_data = f"{self.index}{self.previous_hashes}{self.transactions}{self.timestamp}"
        return hashlib.sha256(block_data.encode()).hexdigest()

    def sign_block(self):
        """Sign the block with RSA private key."""
        return rsa.sign(self.hash.encode(), private_key, 'SHA-256')

    def verify_signature(self):
        """Verify the block's signature using the public key."""
        try:
            rsa.verify(self.hash.encode(), self.signature, public_key)
            return True
        except rsa.VerificationError:
            return False

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
        if new_block.verify_signature():
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
        self.malicious_behavior = {}

    def elect_leader(self):
        """Choose the node with the highest efficiency score as the leader."""
        self.leader = max(self.node_scores, key=self.node_scores.get)
        print(f"[LEADER ELECTION] AI-Selected Leader: {self.leader}")

    def simulate_malicious_nodes(self, probability=0.2):
        """Randomly mark some nodes as malicious with specific attack behaviors."""
        for node in self.nodes:
            if random.random() < probability:
                self.malicious_nodes.add(node)
                self.malicious_behavior[node] = random.choice(["send_fake_tx", "drop_messages"])
        print(f"[SECURITY] Malicious nodes detected: {self.malicious_nodes}")

    def optimize_node_selection(self):
        """Select a subset of high-efficiency nodes for consensus."""
        sorted_nodes = sorted(self.node_scores.items(), key=lambda x: x[1], reverse=True)
        selected_nodes = [node for node, score in sorted_nodes if node not in self.malicious_nodes]
        
        if len(selected_nodes) < self.f + 1:
            print("[SECURITY ALERT] Too many malicious nodes! Consensus may fail.")
        
        return selected_nodes

    def pre_prepare(self, transaction):
        if self.leader is None:
            self.elect_leader()
        
        return {
            node: transaction if node not in self.malicious_nodes else self.inject_fault(transaction, node)
            for node in self.nodes
        }

    def inject_fault(self, transaction, node):
        """Modify transaction behavior if the node is malicious."""
        if self.malicious_behavior[node] == "send_fake_tx":
            return f"FAKE-{transaction}"
        elif self.malicious_behavior[node] == "drop_messages":
            return None  # Simulate message drop
        return transaction

    def prepare(self, message):
        confirmations = {
            node: message for node in self.nodes if node not in self.malicious_nodes and message is not None
        }
        return confirmations

    def commit(self, confirmations):
        valid_votes = len(confirmations) - len(self.malicious_nodes)
        if valid_votes >= 2 * self.f + 1:
            print("[COMMIT] Transaction committed.")
            return True
        print("[COMMIT] Transaction failed due to Byzantine nodes.")
        return False
