import hashlib
import time
import random
import numpy as np
import rsa
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Generate RSA keys for signing
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
        if new_block.verify_signature() and self.validate_block(new_block):
            self.blocks.append(new_block)
            for parent in parent_hashes:
                self.graph[parent].append(new_block.hash)
            self.graph[new_block.hash] = []
        return new_block

    def get_parent_blocks(self):
        if len(self.blocks) < 2:
            return [self.blocks[-1].hash]
        return [block.hash for block in self.blocks[-2:]]

    def validate_block(self, block):
        """Ensure block integrity and proper referencing of parent blocks."""
        if not block.verify_signature():
            print(f"[DAG VALIDATION ERROR] Block {block.index} has invalid signature!")
            return False
        if block.index > 0 and not all(parent in self.graph for parent in block.previous_hashes):
            print(f"[DAG VALIDATION ERROR] Block {block.index} references non-existent parent blocks!")
            return False
        return True
    
    def validate_dag(self):
        """Validate the integrity of the DAG blockchain structure."""
        print("\n[VALIDATING DAG STRUCTURE]")

        for block in self.blocks:
            # Ensure block hash is correct
            if block.hash != block.compute_hash():
                print(f"[ERROR] Block {block.index} has an invalid hash!")
                return False

            # Ensure parent references exist in the blockchain
            for parent in block.previous_hashes:
                if parent not in self.graph:
                    print(f"[ERROR] Block {block.index} references a missing parent!")
                    return False

        print("[SUCCESS] DAG Blockchain is valid!")
        return True


    def visualize_dag(self):
        """Generate a full visual representation of the DAG blockchain."""
        print("\n[DAG Blockchain Structure]")
        for block in self.blocks:
            print(f"Block {block.index} | Hash: {block.hash} | Parents: {block.previous_hashes}")

        dag = nx.DiGraph()
        for block in self.blocks:
            dag.add_node(block.hash, label=f"Block {block.index}")
            for parent in block.previous_hashes:
                dag.add_edge(parent, block.hash)

        plt.figure(figsize=(12, 6))
        pos = nx.spring_layout(dag)
        labels = {node: dag.nodes[node]['label'] for node in dag.nodes}
        nx.draw(dag, pos, with_labels=True, labels=labels, node_color='lightblue', edge_color='gray', node_size=1500, font_size=10)
        plt.title("DAG Blockchain Structure")
        plt.show()

# U-PBFT (Hierarchical Byzantine Fault Tolerance for UAVs)
class UPBFT:
    def __init__(self, nodes, f):
        self.nodes = nodes
        self.f = f  # Max Byzantine nodes tolerated
        self.leader_index = 0  # Index for round-robin leader rotation
        self.malicious_nodes = set()
        self.node_scores = {node: np.random.uniform(0, 1) for node in self.nodes}  # AI-based ranking
        self.performance_metrics = {"total_transactions": 0, "total_time": 0.00001}

    def detect_malicious_nodes(self):
        """Detect and isolate malicious nodes."""
        print("\n[SECURITY] Checking for Byzantine behavior...")

        for node in self.nodes:
            if self.node_scores[node] < 0.3:  # Assume nodes with score < 0.3 are Byzantine
                self.malicious_nodes.add(node)

        print(f"[INFO] Malicious Nodes Detected: {self.malicious_nodes}")


    def elect_leader(self):
        """Rotate leader, ensuring it's not malicious."""
        if self.performance_metrics["total_transactions"] % 10 == 0:
            self.leader_index = (self.leader_index + 1) % len(self.nodes)
        self.leader = self.nodes[self.leader_index]

        if self.leader in self.malicious_nodes:
            print(f"[WARNING] Leader {self.leader} is malicious! Selecting new leader...")
            self.elect_leader()

        print(f"[LEADER ELECTION] Rotated Leader: {self.leader}")

    def optimize_node_selection(self):
        """Select a subset of high-efficiency nodes for consensus."""
        sorted_nodes = sorted(self.node_scores.items(), key=lambda x: x[1], reverse=True)
        selected_nodes = [node for node, score in sorted_nodes if node not in self.malicious_nodes]

        if len(selected_nodes) < self.f + 1:
            print("[SECURITY ALERT] Too many malicious nodes! Consensus may fail.")

        print(f"[INFO] Optimized Node Selection: {selected_nodes}")
        return selected_nodes

    def pre_prepare(self, transaction):
        """Simulate pre-prepare step in PBFT."""
        return f"PrePrepared({transaction})"

    def prepare(self, pre_prepared_msg):
        """Simulate prepare step in PBFT."""
        return f"Prepared({pre_prepared_msg})"

    def commit(self, prepared_msg):
        """Simulate commit step in PBFT."""
        self.performance_metrics["total_transactions"] += 1
        return True

    def get_performance_metrics(self):
        """Calculate TPS & Latency."""
        total_time = max(self.performance_metrics["total_time"], 0.0001)
        tps = self.performance_metrics["total_transactions"] / total_time
        avg_latency = self.performance_metrics["total_time"] / max(1, self.performance_metrics["total_transactions"])
        return {
            "Total Transactions": self.performance_metrics["total_transactions"],
            "Total Time (s)": round(self.performance_metrics["total_time"], 4),
            "TPS (Transactions Per Second)": round(tps, 4),
            "Average Latency (s)": round(avg_latency, 6)
        }

    def simulate_byzantine_failures(self, failure_rate=0.3):
        """Randomly introduce Byzantine failures among nodes."""
        print("\n[SECURITY TEST] Simulating Byzantine Failures...")

        for node in self.nodes:
            if random.random() < failure_rate:
                self.malicious_nodes.add(node)

        print(f"[INFO] Byzantine Nodes Introduced: {self.malicious_nodes}")
