import hashlib
import time
import random
import numpy as np
import rsa
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

(public_key, private_key) = rsa.newkeys(512)

class Block:
    def __init__(self, index, previous_hashes, transactions, timestamp=None):
        self.index = index
        self.previous_hashes = previous_hashes
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.hash = self.compute_hash()
        self.signature = self.sign_block()

    def compute_hash(self):
        block_data = f"{self.index}{self.previous_hashes}{self.transactions}{self.timestamp}"
        return hashlib.sha256(block_data.encode()).hexdigest()

    def sign_block(self):
        return rsa.sign(self.hash.encode(), private_key, 'SHA-256')

    def verify_signature(self):
        try:
            rsa.verify(self.hash.encode(), self.signature, public_key)
            return True
        except rsa.VerificationError:
            return False

class DAGBlockchain:
    def __init__(self, consensus):
        self.consensus = consensus
        self.blocks = []
        self.graph = defaultdict(list)
        self.genesis_block()

    def genesis_block(self):
        genesis = Block(0, [], ["Genesis Block"])
        self.blocks.append(genesis)
        self.graph[genesis.hash] = []

    def add_block(self, transactions, proposer_node):
        print(f"[INFO] 🏗️ Attempting to add block with transactions: {transactions} from {proposer_node}")

        if proposer_node in self.consensus.malicious_nodes:
            print(f"[SECURITY] 🚨 Block rejected! Byzantine proposer {proposer_node} tried to add a block.")
            return None

        parent_hashes = self.get_parent_blocks()
        new_block = Block(len(self.blocks), parent_hashes, transactions)
        print(f"[DEBUG] 🧱 Creating Block {new_block.index}:")
        print(f"        Hash: {new_block.hash}")
        print(f"        Parents: {parent_hashes}")
        print(f"        Transactions: {transactions}")

        if self.check_for_conflicts(new_block):
            print(f"[ERROR] ❌ Block {new_block.index} rejected due to conflicts!")
            return None

        if not new_block.verify_signature():
            print(f"[ERROR] ❌ Block {new_block.index} has an invalid signature!")
            return None

        if not self.validate_block(new_block):
            print(f"[ERROR] ❌ Block {new_block.index} failed DAG validation!")
            return None

        self.blocks.append(new_block)
        for parent in parent_hashes:
            self.graph[parent].append(new_block.hash)
        self.graph[new_block.hash] = []

        print(f"[BLOCK ADDED] ✅ Successfully added Block {new_block.index} by {proposer_node}.")
        print(f"             DAG now has {len(self.blocks)} blocks.")
        return new_block

    def get_parent_blocks(self):
        if len(self.blocks) < 2:
            return [self.blocks[-1].hash]
        return [block.hash for block in self.blocks[-3:]]

    def validate_block(self, block):
        if block.compute_hash() != block.hash:
            print(f"[DAG VALIDATION ERROR] Block {block.index} has an incorrect hash!")
            return False
        if not block.verify_signature():
            print(f"[DAG VALIDATION ERROR] Block {block.index} has invalid signature!")
            return False
        if block.index > 0 and not all(parent in self.graph for parent in block.previous_hashes):
            print(f"[DAG VALIDATION ERROR] Block {block.index} references non-existent parent blocks!")
            return False
        return True

    def validate_dag(self):
        print("\n[VALIDATING DAG STRUCTURE]")
        for block in self.blocks:
            if block.hash != block.compute_hash():
                print(f"[ERROR] Block {block.index} has an invalid hash!")
                return False
            for parent in block.previous_hashes:
                if parent not in self.graph:
                    print(f"[ERROR] Block {block.index} references a missing parent!")
                    return False
        print("[SUCCESS] DAG Blockchain is valid!")
        return True

    def visualize_dag(self, malicious_nodes=None, num_blocks=50):
        """
        Visualize only the last `num_blocks` blocks to keep the diagram readable.
        Example: blockchain.visualize_dag(malicious_nodes=consensus.malicious_nodes, num_blocks=50)
        """

        print("\n[DAG Blockchain Structure Visualization]")

        # 1. Subset blocks (only the last `num_blocks`)
        if len(self.blocks) > num_blocks:
            subset_blocks = self.blocks[-num_blocks:]
        else:
            subset_blocks = self.blocks

        subset_hashes = {blk.hash for blk in subset_blocks}
        dag = nx.DiGraph()

        # 2. Build subgraph using only those blocks (and edges within the subset)
        for blk in subset_blocks:
            dag.add_node(blk.hash, label=f"Block {blk.index}")
            for parent in blk.previous_hashes:
                if parent in subset_hashes:
                    dag.add_edge(parent, blk.hash)

        # 3. Log the subset
        print(f"[INFO] Subset of DAG: {len(subset_blocks)} blocks (out of {len(self.blocks)} total).")
        for b in subset_blocks:
            print(f"  ➡ Block {b.index}: Transactions: {b.transactions}")

        # 4. Draw the subgraph
        plt.figure(figsize=(12, 6))
        pos = nx.spring_layout(dag, seed=42)  # fixed seed for reproducibility
        labels = {node: dag.nodes[node]['label'] for node in dag.nodes}

        node_colors = [
            "red" if node in (malicious_nodes or []) else "lightblue"
            for node in dag.nodes
        ]

        nx.draw(
            dag,
            pos,
            with_labels=True,
            labels=labels,
            node_color=node_colors,
            edge_color="gray",
            node_size=1500,
            font_size=10,
        )
        plt.title(f"DAG Blockchain (Last {num_blocks} Blocks)")

        plt.savefig("dag_structure_subset.png")
        print("[INFO] DAG subset image saved as dag_structure_subset.png")

        plt.show(block=True)

    def check_for_conflicts(self, new_block):
        """
        Detects double-spending attempts in the DAG blockchain by scanning all existing transactions.
        If any transaction in 'new_block' is already present, we consider it a conflict.
        """
        all_transactions = set()
        for blk in self.blocks:
            for tx in blk.transactions:
                # If tx is found again, it's a potential double-spend
                if tx in new_block.transactions:
                    print(f"[SECURITY ALERT] Double-spend detected for transaction {tx}!")
                    return True
                all_transactions.add(tx)
        return False


class UPBFT:
    def __init__(self, nodes, f):
        self.nodes = nodes
        self.f = f
        self.leader_index = 0
        self.malicious_nodes = set()
        self.node_scores = {node: np.random.uniform(0, 1) for node in self.nodes}
        self.performance_metrics = {"total_transactions": 0, "total_time": 0.00001}
        self.leader_rounds = 0
        self.leader = None

    def detect_malicious_nodes(self):
        print("\n[SECURITY] Checking for Byzantine behavior...")
        for node in self.nodes:
            if self.node_scores[node] < 0.3:
                self.malicious_nodes.add(node)
        self.nodes = [node for node in self.nodes if node not in self.malicious_nodes]
        print(f"[INFO] Malicious Nodes Detected: {self.malicious_nodes}")

    def elect_leader(self, rounds=3):
        valid_nodes = [node for node in self.nodes if node not in self.malicious_nodes]
        if not valid_nodes:
            print("[SECURITY ALERT] ❌ No valid leaders left! Consensus halted.")
            return None

        if self.leader and self.leader_rounds < rounds:
            self.leader_rounds += 1
            return self.leader

        self.leader_rounds = 1
        self.leader_index = (self.leader_index + 1) % len(valid_nodes)
        self.leader = valid_nodes[self.leader_index]
        print(f"[LEADER ELECTION] ✅ New Leader: {self.leader}")
        return self.leader

    def optimize_node_selection(self):
        sorted_nodes = sorted(self.node_scores.items(), key=lambda x: x[1], reverse=True)
        selected_nodes = [node for node, score in sorted_nodes if node not in self.malicious_nodes]
        if len(selected_nodes) < self.f + 1:
            print("[SECURITY ALERT] Too many malicious nodes! Consensus may fail.")
        print(f"[INFO] Optimized Node Selection: {selected_nodes}")
        return selected_nodes

    def pre_prepare(self, transaction):
        return f"PrePrepared({transaction})"

    def prepare(self, pre_prepared_msg):
        return f"Prepared({pre_prepared_msg})"

    def commit(self, prepared_msg):
        self.performance_metrics["total_transactions"] += 1
        return True

    def get_performance_metrics(self):
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
        print("\n[SECURITY TEST] 🔄 Simulating Byzantine Failures...")
        attacked_transactions = []
        new_byzantine_nodes = set()
        for node in self.nodes:
            if random.random() < failure_rate:
                new_byzantine_nodes.add(node)
                fake_tx = f"FakeTx-{node}"
                attacked_transactions.append(fake_tx)
        if new_byzantine_nodes:
            print(f"[ATTACK] 🚨 Byzantine nodes {new_byzantine_nodes} attempting double-spend attack on {attacked_transactions}!")
        self.malicious_nodes.update(new_byzantine_nodes)
        self.nodes = [n for n in self.nodes if n not in self.malicious_nodes]
        print(f"[INFO] Updated Byzantine Nodes: {self.malicious_nodes}")

    def detect_byzantine_behavior(self):
        print("\n[SECURITY CHECK] Scanning for Byzantine behavior...")
        for node in self.malicious_nodes:
            print(f"[ALERT] Detected Byzantine activity from: {node}")
        print("[SECURITY CHECK] Byzantine analysis completed.")
