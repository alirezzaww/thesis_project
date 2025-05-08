import time
from src.consensus.hybrid_consensus import UPBFT
from src.consensus.dag_blockchain import DAGBlockchain
from src.consensus.trust_model import TrustModel

# Initialize Trust Model
trust_model = TrustModel(nodes=["Node1", "Node2", "Node3", "Node4"])

# Initialize Consensus with Trust Model
consensus = UPBFT(nodes=["Node1", "Node2", "Node3", "Node4"], f=1, trust_model=trust_model)

# Initialize Blockchain
blockchain = DAGBlockchain(consensus=consensus)

def benchmark():
    """Measures Transactions Per Second (TPS), success rate, and Execution Time"""
    start_time = time.perf_counter()
    total_transactions = 10000
    success_count = 0

    for _ in range(total_transactions):
        leader = consensus.elect_leader(blockchain)
        if leader:
            result = blockchain.add_block(["Tx"], leader)
            if result:
                success_count += 1

    execution_time = max(time.perf_counter() - start_time, 0.1)
    TPS = success_count / execution_time
    success_rate = (success_count / total_transactions) * 100

    print(f"[Performance] 📊 TPS: {TPS:.2f}")
    print(f"[Performance] ✅ Success Rate: {success_rate:.2f}%")
    print(f"[Performance] ⏱️ Total Execution Time: {execution_time:.2f} seconds")

    # Export benchmark results to CSV
    import csv
    with open("benchmark_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["TPS", "Success Rate (%)", "Execution Time (s)"])
        writer.writerow([round(TPS, 2), round(success_rate, 2), round(execution_time, 2)])

    # Export trust scores to JSON
    import json
    with open("trust_scores_snapshot.json", mode="w") as f:
        json.dump(trust_model.trust_scores, f, indent=2)

    print("[EXPORT] 📁 Benchmark results saved to benchmark_log.csv")
    print("[EXPORT] 📁 Trust scores snapshot saved to trust_scores_snapshot.json")

if __name__ == "__main__":
    benchmark()
