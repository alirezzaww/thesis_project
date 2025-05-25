import numpy as np
import time
import joblib
import os

class TrustModel:
    def __init__(self, nodes):
        """Initialize trust scores and proposal tracking for each node."""
        self.trust_scores = {}
        for node in nodes:
            base = np.random.uniform(0.4, 0.7)
            noise = np.random.normal(0, 0.05)
            self.trust_scores[node] = round(min(1.0, max(0.25, base + noise)), 4)
        self.last_activity = {node: time.time() for node in nodes}  # Track last activity for trust decay
        self.misbehavior_count = {node: 0 for node in nodes}  # Track violations
        self.successful_proposals = {node: 0 for node in nodes}  # ✅ Track successful block proposals
        self.malicious_nodes = set()  # ✅ Maintain a list of blacklisted nodes

        # Load the fraud detection model if available
        model_path = "fraud_detection_model.pkl"
        if os.path.exists(model_path):
            try:
                self.fraud_model = joblib.load(model_path)
            except Exception as e:
                print(f"[TRUST_MODEL] Warning: failed to load fraud model: {e}")
                self.fraud_model = None
        else:
            print(f"[TRUST_MODEL] Fraud model file not found at {model_path}.")
            self.fraud_model = None

        self.node_model = None
        node_model_path = "node_selection_model.pkl"
        if os.path.exists(node_model_path):
            try:
                self.node_model = joblib.load(node_model_path)
                print("[TRUST_MODEL] Node selection model loaded.")
            except Exception as e:
                print(f"[TRUST_MODEL] Warning: failed to load node selection model: {e}")

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
        self.trust_scores[node] = max(0.25, min(1.0, new_trust))  # Raise trust floor from 0.1 to 0.25
        self.last_activity[node] = current_time

    def recover_trust(self, node):
        """Gradually restore trust for blacklisted nodes after cooldown."""
        if node in self.malicious_nodes:
            print(f"[RECOVERY] ⏳ Node {node} is under cooldown. Gradually restoring trust.")
            self.trust_scores[node] += 0.05  # Small trust recovery over time
            if self.trust_scores[node] > 0.35:  # Restore when trust is high enough
                print(f"[RECOVERY] ✅ Node {node} has recovered and is removed from blacklist.")
                self.malicious_nodes.remove(node)

    def get_trust_score(self, node):
        """Retrieve the trust score of a node."""
        return self.trust_scores.get(node, 0.5)  # Default to neutral trust

    def get_composite_score(self, node, energy=1.0, tx_success_rate=1.0, fraud_rate=0.0):
        """
        Compute a composite node score using either ML model or weighted formula.
        """
        trust = self.get_trust_score(node)
        if self.node_model:
            try:
                features = np.array([[trust, energy, tx_success_rate, fraud_rate]])
                return float(self.node_model.predict(features)[0])
            except Exception as e:
                print(f"[TRUST_MODEL] Warning during ML prediction: {e}")
        # Fallback to weighted scoring
        α, β, γ, δ = 0.4, 0.3, 0.2, 0.1
        score = (α * trust) + (β * energy) + (γ * tx_success_rate) - (δ * fraud_rate)
        return round(score, 4)

    def get_malicious_nodes(self):
        """Detect and penalize nodes with very low trust scores, but allow recovery."""
        malicious_nodes = set()

        for node, score in self.trust_scores.items():
            if score < 0.3:
                self.misbehavior_count[node] += 1  
                penalty_factor = 1.1 ** self.misbehavior_count[node]  # Slower exponential penalty
                self.trust_scores[node] = max(0.25, score / penalty_factor)  # Raise floor to 0.25

                if self.misbehavior_count[node] > 5:  # ✅ Allow recovery after multiple failures
                    print(f"[SECURITY ALERT] 🔄 Node {node} has served penalty time. Removing from blacklist.")
                    self.misbehavior_count[node] = 0  # Reset misbehavior counter
                    continue  

                malicious_nodes.add(node)

        self.malicious_nodes = malicious_nodes
        return malicious_nodes

    def score_transaction(self, tx_features):
        """Return predicted fraud probability for a transaction."""
        if self.fraud_model is None:
            return 0.0
        # Assume tx_features is a feature vector list or array
        probs = self.fraud_model.predict_proba([tx_features])
        # Return probability of the positive (fraudulent) class
        return float(probs[0][1])

    def prepare_features(self, tx):
        """Convert raw transaction data into model input features."""
        # TODO: adapt this to your model's expected feature format
        return tx

    def get_reputation_tier(self, node):
        """Categorize node reputation into tiers."""
        score = self.get_trust_score(node)
        if score >= 0.85:
            return "High"
        elif score >= 0.6:
            return "Medium"
        else:
            return "Low"