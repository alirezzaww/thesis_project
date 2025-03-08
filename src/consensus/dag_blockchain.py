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
    def __init__(self, index, previous_hashes, transactions, proposer, timestamp=None):
        self.index = index
        self.previous_hashes = previous_hashes  # Multiple parents in DAG
        self.transactions = transactions
        self.proposer = proposer
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
        """Creates a genesis block to initialize the DAG."""
        genesis_block = Block(index=0, previous_hashes=[], transactions=["Genesis Block"], proposer="System")
        self.blocks.append(genesis_block)
        self.graph[genesis_block.hash] = []
        print("[INFO] Genesis Block Created.")

    def add_block(self, transactions, proposer_node):
        """Adds a new block to the DAG, ensuring proposer is not Byzantine."""
        print(f"[INFO] 🏗️ Attempting to add block with transactions: {transactions} from {proposer_node}")

        if proposer_node in self.consensus.malicious_nodes:
            print(f"[SECURITY] 🚨 Block rejected! Byzantine proposer {proposer_node} tried to add a block.")
            return None

        parent_hashes = self.get_parent_blocks()
        new_block = Block(len(self.blocks), parent_hashes, transactions, proposer_node)

        print(f"[DEBUG] 🧱 Creating Block {new_block.index}:")
        print(f"        Hash: {new_block.hash}")
        print(f"        Parents: {parent_hashes}")
        print(f"        Transactions: {transactions}")

        if self.check_for_conflicts(new_block):
            print(f"[ERROR] ❌ Block {new_block.index} rejected due to conflicts!")
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
        """Returns parent blocks for DAG structure."""
        if len(self.blocks) < 2:
            return [self.blocks[-1].hash]
        return [block.hash for block in self.blocks[-3:]]

    def validate_block(self, block):
        """Validates a single block in the DAG."""
        if block.compute_hash() != block.hash:
            print(f"[DAG VALIDATION ERROR] Block {block.index} has an incorrect hash!")
            return False
        if block.index > 0 and not all(parent in self.graph for parent in block.previous_hashes):
            print(f"[DAG VALIDATION ERROR] Block {block.index} references non-existent parent blocks!")
            return False
        return True

    def validate_dag(self):
        """Validates the entire DAG structure."""
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
        """Visualize only the last `num_blocks` blocks to keep the diagram readable."""
        print("\n[DAG Blockchain Structure Visualization]")

        # Subset the last `num_blocks`
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

        nx.draw(
            dag, pos, with_labels=True, labels=labels,
            node_color=node_colors, edge_color="gray",
            node_size=1500, font_size=10
        )
        plt.title(f"DAG Blockchain (Last {num_blocks} Blocks)")

        plt.savefig("dag_structure_subset.png")
        print("[INFO] DAG subset image saved as dag_structure_subset.png")

        plt.show(block=True)

    def check_for_conflicts(self, new_block):
        """Detects double-spending attempts in the DAG blockchain."""
        all_transactions = set()
        for blk in self.blocks:
            for tx in blk.transactions:
                if tx in new_block.transactions:
                    print(f"[SECURITY ALERT] Double-spend detected for transaction {tx}!")
                    return True
                all_transactions.add(tx)
        return False
