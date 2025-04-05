import numpy as np
import time

class TrustModel:
    def __init__(self, nodes):
        """Initialize trust scores and proposal tracking for each node."""
        self.trust_scores = {node: np.random.uniform(0.5, 1.0) for node in nodes}
        self.last_activity = {node: time.time() for node in nodes}  # Track last activity for trust decay
        self.misbehavior_count = {node: 0 for node in nodes}  # Track violations
        self.successful_proposals = {node: 0 for node in nodes}  # ✅ Track successful block proposals
        self.malicious_nodes = set()  # ✅ Maintain a list of blacklisted nodes

    def update_trust_score(self, node, successful_blocks, total_attempts):
        """Dynamically update trust scores based on successful participation and recovery logic."""
        current_time = time.time()

        if total_attempts == 0:
            return  # Avoid division by zero

        success_ratio = successful_blocks / total_attempts
        time_since_last_block = current_time - self.last_activity.get(node, current_time)
        decay_factor = np.exp(-0.02 * time_since_last_block)  # Slower decay

        previous_trust = self.trust_scores.get(node, 0.5)

        # **Gradual Trust Recovery**
        if success_ratio > 0.5:
            trust_gain = (0.1 * success_ratio) + 0.05
        else:
            trust_gain = -0.02 * self.misbehavior_count.get(node, 1)

        # **Allow slow recovery if trust is above 0.25**
        if self.trust_scores[node] < 0.35:
            trust_gain += 0.05

        new_trust = (0.8 * previous_trust) + (0.2 * (previous_trust + trust_gain))
        self.trust_scores[node] = max(0.1, min(1.0, new_trust))
        self.last_activity[node] = current_time

    def recover_trust(self, node):
        """Gradually restore trust for blacklisted nodes after cooldown."""
        if node in self.malicious_nodes:
            print(f"[RECOVERY] ⏳ Node {node} is under cooldown. Gradually restoring trust.")
            self.trust_scores[node] += 0.05  # Small trust recovery over time
            if self.trust_scores[node] > 0.4:  # Restore when trust is high enough
                print(f"[RECOVERY] ✅ Node {node} has recovered and is removed from blacklist.")
                self.malicious_nodes.remove(node)

    def get_trust_score(self, node):
        """Retrieve the trust score of a node."""
        return self.trust_scores.get(node, 0.5)  # Default to neutral trust

    def get_malicious_nodes(self):
        """Detect and penalize nodes with very low trust scores, but allow recovery."""
        malicious_nodes = set()

        for node, score in self.trust_scores.items():
            if score < 0.3:
                self.misbehavior_count[node] += 1  
                penalty_factor = 1.1 ** self.misbehavior_count[node]  # Slower exponential penalty
                self.trust_scores[node] = max(0.1, score / penalty_factor)  # Apply penalty

                if self.misbehavior_count[node] > 5:  # ✅ Allow recovery after multiple failures
                    print(f"[SECURITY ALERT] 🔄 Node {node} has served penalty time. Removing from blacklist.")
                    self.misbehavior_count[node] = 0  # Reset misbehavior counter
                    continue  

                malicious_nodes.add(node)

        self.malicious_nodes = malicious_nodes
        return malicious_nodes
