from collections import defaultdict
import hashlib
import time
import networkx as nx
import matplotlib.pyplot as plt
import rsa

# Generate RSA keys for signing
(public_key, private_key) = rsa.newkeys(512)

class Block:
    """Represents a single block in the DAG blockchain."""
    def __init__(self, index, previous_hashes, transactions, proposer, trust_score=0.5, timestamp=None):
        self.index = index
        self.previous_hashes = previous_hashes  # Multiple parents in DAG
        self.transactions = transactions
        self.proposer = proposer
        self.trust_score = trust_score  # ✅ FIX: Added trust_score to Block
        self.timestamp = timestamp or time.time()
        self.hash = self.compute_hash()
        self.signature = self.sign_block()

    def compute_hash(self):
        """Computes SHA-256 hash of block data."""
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

class DAGBlockchain:
    def __init__(self, consensus):
        self.consensus = consensus
        self.blocks = []
        self.graph = defaultdict(list)
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            previous_hashes=[],
            transactions=["Genesis Block"],
            proposer="System",
            trust_score=1.0
        )
        self.blocks.append(genesis_block)
        self.graph[genesis_block.hash] = []
        print("[INFO] ✅ Genesis Block Created with Trust Score 1.0.")

    def get_parent_blocks(self):
        if len(self.blocks) < 2:
            return [self.blocks[-1].hash]

        parent_candidates = self.blocks[-10:]  # Analyze the last 10 blocks
        now = time.time()

        def score_block(b):
            time_decay = max(0.1, 1.0 / (1.0 + (now - b.timestamp)))
            tx_volume = len(b.transactions)
            trust_score = b.trust_score
            return trust_score * time_decay * (tx_volume + 1)

        scored_parents = sorted(
            parent_candidates,
            key=score_block,
            reverse=True
        )

        top_k = 3  # number of parents to attach
        return [block.hash for block in scored_parents[:top_k]]

    def add_block(self, transactions, proposer_node):
        print(f"[INFO] 🏗️ Attempting to add block with transactions: {transactions} from {proposer_node}")

        if proposer_node is None:
            print("[ERROR] ❌ Proposer node is None. Skipping block addition.")
            return None

        if proposer_node in self.consensus.malicious_nodes:
            print(f"[SECURITY] 🚨 Block rejected! Byzantine proposer {proposer_node} detected.")
            return None

        parent_hashes = self.get_parent_blocks()
        if not parent_hashes:
            print("[ERROR] ❌ Block rejected! No valid parent blocks found.")
            return None

        trust_score = self.consensus.trust_model.trust_scores.get(proposer_node, 0.5)
        new_block = Block(len(self.blocks), parent_hashes, transactions, proposer_node, trust_score)
        validation_result = self.validate_block(new_block)

        if validation_result == "RETRY":
            print(f"[SECURITY] 🔄 Block {new_block.index} ALMOST passed, retrying validation...")
            return None

        if not validation_result:
            self.consensus.trust_model.misbehavior_count[proposer_node] += 1
            if self.consensus.trust_model.misbehavior_count[proposer_node] >= 3:
                print(f"[SECURITY ALERT] 🚨 Proposer {proposer_node} blacklisted due to repeated failures.")
                self.consensus.malicious_nodes.add(proposer_node)
            # ✅ Attempt trust recovery for proposer if recently blacklisted
            if proposer_node in self.consensus.malicious_nodes:
                if self.consensus.trust_model.trust_scores[proposer_node] > 0.35:
                    print(f"[RECOVERY] ✅ Node {proposer_node} restored from malicious list.")
                    self.consensus.malicious_nodes.remove(proposer_node)
            return None

        self.blocks.append(new_block)
        for parent in parent_hashes:
            self.graph[parent].append(new_block.hash)
        self.graph[new_block.hash] = []

        success_ratio = 0.75 if validation_result else 0.5
        self.consensus.trust_model.update_trust_score(proposer_node, successful_blocks=success_ratio, total_attempts=5)
        print(f"[BLOCK ADDED] ✅ Block {new_block.index} by {proposer_node} (Trust Score: {trust_score:.2f}).")
        return new_block

    def validate_block(self, block):
        if block.compute_hash() != block.hash:
            print(f"[DAG VALIDATION ERROR] ❌ Block {block.index} has an incorrect hash!")
            return False
        if not block.verify_signature():
            print(f"[SECURITY ERROR] ❌ Block {block.index} has an invalid signature!")
            return False

        total_weight = sum(b.trust_score for b in self.blocks) + 1e-9
        recent_blocks = self.blocks[-10:] if len(self.blocks) > 10 else self.blocks
        avg_trust_score = sum(b.trust_score for b in recent_blocks) / max(1, len(recent_blocks))
        base_threshold = max(total_weight * 0.50, avg_trust_score * 0.70)

        if not hasattr(self, 'retry_counts'):
            self.retry_counts = {}

        block_id = block.index
        if block_id not in self.retry_counts:
            self.retry_counts[block_id] = 0

        retry_attempts = self.retry_counts[block_id]
        adjusted_threshold = base_threshold * max(0.75, min(1.2, len(self.blocks) / 50))
        retry_threshold = adjusted_threshold * (0.92 - 0.02 * retry_attempts)
        parent_weight = sum(b.trust_score for b in self.blocks if b.hash in block.previous_hashes)

        if parent_weight < adjusted_threshold:
            if parent_weight >= retry_threshold:
                if retry_attempts < 3:
                    self.retry_counts[block.index] += 1
                    print(f"[SECURITY] 🔄 Block {block.index} ALMOST passed, retrying (attempt {retry_attempts + 1}/3)...")
                    return "RETRY"
                else:
                    trust_model = self.consensus.trust_model
                    if parent_weight >= retry_threshold * 0.95:
                        print(f"[SECURITY] ⚠️ Block {block.index} FORCED ACCEPTANCE after 3 retries!")
                        return True
                    else:
                        print(f"[SECURITY] ❌ Block {block.index} permanently rejected after {retry_attempts} retries!")
                        trust_model.misbehavior_count[block.proposer] += 1
                        if trust_model.misbehavior_count[block.proposer] >= 3:
                            print(f"[SECURITY ALERT] 🚨 Proposer {block.proposer} penalized for repeated failures. Reducing trust score.")
                            trust_model.trust_scores[block.proposer] *= 0.7
                            trust_model.misbehavior_count[block.proposer] = 0
                            if trust_model.trust_scores[block.proposer] < 0.2:
                                print(f"[SECURITY ALERT] 🚨 Proposer {block.proposer} blacklisted due to critically low trust score.")
                                trust_model.malicious_nodes.add(block.proposer)
                        return False
            else:
                print(f"[SECURITY] ❌ Block {block.index} rejected! Trust weight too low ({parent_weight:.2f} < {adjusted_threshold:.2f}).")
                return False

        print(f"[DAG VALIDATION] ✅ Block {block.index} is valid.")
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
        print("[SUCCESS] ✅ DAG Blockchain is valid!")
        return True

    def visualize_dag(self, malicious_nodes=None, num_blocks=50):
        print("\n[DAG Blockchain Structure Visualization]")
        subset_blocks = self.blocks[-num_blocks:] if len(self.blocks) > num_blocks else self.blocks
        subset_hashes = {blk.hash for blk in subset_blocks}
        dag = nx.DiGraph()

        for blk in subset_blocks:
            dag.add_node(blk.hash, label=f"Block {blk.index}")
            for parent in blk.previous_hashes:
                if parent in subset_hashes:
                    dag.add_edge(parent, blk.hash)

        print(f"[INFO] Subset of DAG: {len(subset_blocks)} blocks (out of {len(self.blocks)} total).")
        for b in subset_blocks:
            print(f"  ➡ Block {b.index}: Transactions: {b.transactions}")

        plt.figure(figsize=(12, 6))
        pos = nx.spring_layout(dag, seed=42)
        labels = {node: dag.nodes[node]['label'] for node in dag.nodes}

        node_colors = ["red" if node in (malicious_nodes or []) else "lightblue" for node in dag.nodes]
        nx.draw(dag, pos, with_labels=True, labels=labels,
                node_color=node_colors, edge_color="gray",
                node_size=1500, font_size=10)
        plt.title(f"DAG Blockchain (Last {num_blocks} Blocks)")
        plt.savefig("dag_structure_subset.png")
        print("[INFO] DAG subset image saved as dag_structure_subset.png")
        plt.show(block=True)

    def check_for_conflicts(self, new_block):
        all_transactions = set()
        for blk in self.blocks:
            for tx in blk.transactions:
                if tx in new_block.transactions:
                    if time.time() - blk.timestamp < 5:
                        print(f"[SECURITY ALERT] Double-spend detected for transaction {tx}! Retrying after leader change...")
                        return "RETRY"
                    return True
        return False

    def get_performance_metrics(self):
        """Proxy to retrieve performance metrics from the consensus layer."""
        total_time = max(self.consensus.performance_metrics["total_time"], 0.0001)
        total_tx = self.consensus.performance_metrics["total_transactions"]
        tps = total_tx / total_time
        avg_latency = total_time / max(1, total_tx)

        return {
            "Total Transactions": total_tx,
            "Total Time (s)": round(total_time, 4),
            "TPS (Transactions Per Second)": round(tps, 4),
            "Average Latency (s)": round(avg_latency, 6)
        }
