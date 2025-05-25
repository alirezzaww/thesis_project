import random
import numpy as np
import time

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
        self.skipped_count = {node: 0 for node in self.nodes}

    def detect_malicious_nodes(self):
        """Detect Byzantine nodes using reputation scores."""
        print("\n[SECURITY] Checking for Byzantine behavior...")
        for node in self.nodes:
            if self.node_scores[node] < 0.3:  # Nodes with score <0.3 are considered Byzantine
                self.malicious_nodes.add(node)
        
        self.nodes = [node for node in self.nodes if node not in self.malicious_nodes]
        print(f"[INFO] Malicious Nodes Detected: {self.malicious_nodes}")



    def elect_leader(self, blockchain, rounds=3, top_n=3):
        """
        Enhanced leader selection with trust recovery and leader rotation:
        - Excludes blacklisted nodes but allows recovery.
        - Uses trust-weighted voting for selection.
        - Implements leader rotation to prevent starvation.
        """

        # ✅ Step 1: Apply trust decay for inactive nodes
        for node in self.nodes:
            last_activity = self.trust_model.last_activity.get(node, time.time())
            time_since_last_activity = max(1, time.time() - last_activity)
            decay_factor = np.exp(-0.005 * time_since_last_activity)
            self.trust_model.trust_scores[node] *= decay_factor

        # ✅ Step 2: Allow recovery of blacklisted nodes
        restored_nodes = []
        for node in self.trust_model.malicious_nodes.copy():
            if self.trust_model.trust_scores[node] > 0.35:
                print(f"[SECURITY ALERT] 🔄 Restoring proposer {node} after cooldown.")
                self.trust_model.malicious_nodes.remove(node)
                restored_nodes.append(node)

        if restored_nodes:
            return self.elect_leader(blockchain, rounds, top_n)

        # ✅ Floor trust scores to avoid float underflow
        for node in self.nodes:
            if self.trust_model.trust_scores[node] < 0.25:
                self.trust_model.trust_scores[node] = 0.25

        # ✅ DEBUG PRINTS HERE
        print("\n[DEBUG] 🔍 Starting Leader Election")
        print("[DEBUG] Trust Scores:", self.trust_model.trust_scores)
        print("[DEBUG] Malicious Nodes:", self.trust_model.malicious_nodes)
        print("[DEBUG] Successful Proposals:", self.trust_model.successful_proposals)
        print("[DEBUG] Blockchain Length:", len(blockchain.blocks))

        # ✅ Step 3: Filter valid nodes
        valid_nodes = sorted(
            [
                node for node in self.nodes
                if node not in self.trust_model.malicious_nodes
                and self.trust_model.get_trust_score(node) > 0.3
                and self.trust_model.successful_proposals.get(node, 0) >= (0 if len(blockchain.blocks) < 5 else 2)
            ],
            key=lambda x: self.trust_model.get_trust_score(x),
            reverse=True
        )

        print("[DEBUG] Valid Candidates:", valid_nodes)

        if not valid_nodes:
            print("[SECURITY ALERT] ❌ No possible leaders available. Trying fallback with relaxed threshold...")

            # Fallback attempt with lower threshold (e.g. 0.2)
            fallback_candidates = sorted(
                [
                    node for node in self.nodes
                    if node not in self.trust_model.malicious_nodes
                    and self.trust_model.get_trust_score(node) > 0.2
                ],
                key=lambda x: self.trust_model.get_trust_score(x),
                reverse=True
            )

            if fallback_candidates:
                self.leader = fallback_candidates[0]
                print(f"[FALLBACK] 🛠️ Elected fallback leader: {self.leader} (Trust Score: {self.trust_model.get_trust_score(self.leader):.2f})")
                return self.leader

            # Proceed with performance-based fallback if needed
            print("[SECURITY ALERT] ❌ No possible leaders available. Halting consensus for this round.")
            # ✅ Step 3.5: Try fallback leader if TPS is too low
            metrics = blockchain.get_performance_metrics()
            if metrics["TPS (Transactions Per Second)"] < 10 and self.leader in self.nodes:
                print(f"[PERFORMANCE ALERT] 🔁 TPS below threshold. Re-electing leader to improve throughput.")
                valid_candidates = [n for n in self.nodes if n != self.leader and n not in self.trust_model.malicious_nodes]
                if valid_candidates:
                    self.leader = random.choice(valid_candidates)
                    self.leader_rounds = 1
                    print(f"[RE-ELECTION] 🆕 Leader after TPS drop: {self.leader}")
                    return self.leader
            return None

        # ✅ Step 4: Maintain current leader if still qualified
        if self.leader and self.leader_rounds < rounds:
            if self.trust_model.get_trust_score(self.leader) > 0.6:
                self.leader_rounds += 1
                print(f"[DEBUG] 🔁 Keeping Current Leader: {self.leader}")
                return self.leader

        self.leader_rounds = 1

        # ✅ Step 5: Elect new leader using composite scoring
        def compute_node_score(node):
            energy = getattr(self.trust_model, "energy", {}).get(node, 1.0)
            success_rate = self.trust_model.successful_proposals.get(node, 0) / max(1, len(self.trust_model.successful_proposals))
            fraud_rate = self.trust_model.misbehavior_count.get(node, 0) / 10  # Normalize
            return self.trust_model.get_composite_score(node, energy, success_rate, fraud_rate)

        scored_candidates = sorted(valid_nodes, key=compute_node_score, reverse=True)
        top_candidates = scored_candidates[:top_n]

        # Prioritize nodes with fewer skips for fairness
        top_candidates = sorted(top_candidates, key=lambda x: self.skipped_count.get(x, 0))

        self.leader = top_candidates[0]
        self.skipped_count[self.leader] = 0
        for node in self.nodes:
            if node != self.leader:
                self.skipped_count[node] += 1

        print("[DEBUG] Skipped Counts:", self.skipped_count)
        print(f"[LEADER ELECTION] ✅ New Leader: {self.leader} (Trust Score: {self.trust_model.get_trust_score(self.leader):.2f})")
        return self.leader

    def optimize_node_selection(self):
        """Select nodes based on AI-composite trust scoring model."""
        def compute_node_score(node):
            energy = getattr(self.trust_model, "energy", {}).get(node, 1.0)
            success_rate = self.trust_model.successful_proposals.get(node, 0) / max(1, len(self.trust_model.successful_proposals))
            fraud_rate = self.trust_model.misbehavior_count.get(node, 0) / 10  # Normalize
            return self.trust_model.get_composite_score(node, energy, success_rate, fraud_rate)

        scored_nodes = sorted(
            [node for node in self.nodes if node not in self.malicious_nodes],
            key=compute_node_score,
            reverse=True
        )

        selected_nodes = scored_nodes[:max(1, self.f + 1)]
        # Ensure minimum committee size of f+1
        min_committee = self.f + 1
        if len(selected_nodes) < min_committee:
            # Fallback to all non-malicious nodes
            selected_nodes = [n for n in self.nodes if n not in self.malicious_nodes]
            print(f"[CONSENSUS] Fallback: using all non-malicious nodes for committee: {selected_nodes}")
        
        print(f"[INFO] Selected Nodes Based on Composite Scoring: {selected_nodes}")
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

    def reply(self, committed_msg):
        """Simulate the reply step in U-PBFT."""
        return f"Replied({committed_msg})"

    def run_consensus(self, transaction, blockchain):
        """Orchestrate a full U-PBFT consensus round for a transaction."""
        # Detect and remove Byzantine nodes before consensus
        self.detect_malicious_nodes()
        # Elect a leader
        leader = self.elect_leader(blockchain)
        if leader is None:
            raise Exception("No leader available for consensus")
        self.leader = leader
        # Pre-prepare phase
        pre_msg = self.pre_prepare(transaction)
        # Prepare phase: collect prepare messages from selected nodes
        participants = self.optimize_node_selection()
        prepare_msgs = [self.prepare(pre_msg) for _ in participants]
        if len(prepare_msgs) < 2 * self.f + 1:
            raise Exception("Prepare phase failed: insufficient prepares")
        # Commit phase: collect commit results
        commit_results = [self.commit(msg) for msg in prepare_msgs]
        if sum(1 for res in commit_results if res) < 2 * self.f + 1:
            raise Exception("Commit phase failed: insufficient commits")
        # Reply phase
        reply = self.reply(pre_msg)
        return reply

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

   
