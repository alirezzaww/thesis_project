import random
import numpy as np

class UPBFT:
    def __init__(self, nodes, f, trust_model=None):  # ✅ Allow optional trust_model
        self.nodes = nodes
        self.f = f
        self.trust_model = trust_model  # ✅ Store trust_model if provided
        self.leader_index = 0
        self.malicious_nodes = set()
        self.node_scores = {node: np.random.uniform(0, 1) for node in self.nodes}
        self.performance_metrics = {"total_transactions": 0, "total_time": 0.00001}
        self.leader_rounds = 0
        self.leader = None

    def detect_malicious_nodes(self):
        """Detect Byzantine nodes using reputation scores."""
        print("\n[SECURITY] Checking for Byzantine behavior...")
        for node in self.nodes:
            if self.node_scores[node] < 0.3:  # Nodes with score <0.3 are considered Byzantine
                self.malicious_nodes.add(node)
        
        self.nodes = [node for node in self.nodes if node not in self.malicious_nodes]
        print(f"[INFO] Malicious Nodes Detected: {self.malicious_nodes}")

    def elect_leader(self, rounds=3):
        """Select a leader for a given number of rounds. If leader is malicious, elect a new one."""
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
        """Prioritize non-Byzantine nodes for consensus decision-making."""
        sorted_nodes = sorted(self.node_scores.items(), key=lambda x: x[1], reverse=True)
        selected_nodes = [node for node, score in sorted_nodes if node not in self.malicious_nodes]

        if len(selected_nodes) < self.f + 1:
            print("[SECURITY ALERT] ❌ Too many malicious nodes! Consensus may fail.")
        
        print(f"[INFO] Optimized Node Selection: {selected_nodes}")
        return selected_nodes

    def pre_prepare(self, transaction):
        """Simulate the pre-prepare step in PBFT."""
        return f"PrePrepared({transaction})"

    def prepare(self, pre_prepared_msg):
        """Simulate the prepare step in PBFT."""
        return f"Prepared({pre_prepared_msg})"

    def commit(self, prepared_msg):
        """Simulate the commit step in PBFT."""
        self.performance_metrics["total_transactions"] += 1
        return True

    def get_performance_metrics(self):
        """Calculate and return blockchain performance metrics."""
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
        """Introduce Byzantine failures randomly in the network."""
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
        """Monitor and report detected Byzantine nodes."""
        print("\n[SECURITY CHECK] Scanning for Byzantine behavior...")
        for node in self.malicious_nodes:
            print(f"[ALERT] 🚨 Detected Byzantine activity from: {node}")
        print("[SECURITY CHECK] ✅ Byzantine analysis completed.")
