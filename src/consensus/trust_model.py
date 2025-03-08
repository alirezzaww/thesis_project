import numpy as np

class TrustModel:
    def __init__(self, nodes):
        self.trust_scores = {node: np.random.uniform(0.5, 1.0) for node in nodes}

    def get_malicious_nodes(self):
        """Detect nodes with low trust scores."""
        return {node for node, score in self.trust_scores.items() if score < 0.3}

    def optimize_node_selection(self):
        """Select only high-trust nodes."""
        sorted_nodes = sorted(self.trust_scores.items(), key=lambda x: x[1], reverse=True)
        return [node for node, score in sorted_nodes if score >= 0.3]
