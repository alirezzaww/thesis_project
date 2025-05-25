import sys
import os
# Ensure project root is on Python path for src package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import time
import csv
import json

from src.consensus.hybrid_consensus import UPBFT
from src.consensus.dag_blockchain import DAGBlockchain
from src.consensus.trust_model import TrustModel

def benchmark(num_nodes=4, total_transactions=10000):
    """Measures Transactions Per Second (TPS), success rate, and execution time."""
    # Initialize nodes and components
    nodes = [f"Node{i}" for i in range(1, num_nodes + 1)]
    trust_model = TrustModel(nodes)
    consensus = UPBFT(nodes=nodes, f=1, trust_model=trust_model)
    blockchain = DAGBlockchain(consensus=consensus)

    # Run transactions
    start_time = time.perf_counter()
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

    # Print metrics
    print(f"[Performance] 📊 TPS: {TPS:.2f}")
    print(f"[Performance] ✅ Success Rate: {success_rate:.2f}%")
    print(f"[Performance] ⏱️ Total Execution Time: {execution_time:.2f} seconds")

    # Export benchmark results to CSV
    with open("benchmark_log.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TPS", "Success Rate (%)", "Execution Time (s)"])
        writer.writerow([round(TPS, 2), round(success_rate, 2), round(execution_time, 2)])

    # Export trust model snapshot to JSON
    with open("trust_model_snapshot.json", mode="w") as f:
        json.dump({
            "trust_scores": trust_model.trust_scores,
            "malicious_nodes": list(trust_model.malicious_nodes)
        }, f, indent=2)
    print("[EXPORT] 📁 Benchmark results saved to benchmark_log.csv")
    print("[EXPORT] 📁 Trust model snapshot saved to trust_model_snapshot.json")

    # Export extended benchmark data to JSON
    extended_data = {
        "TPS": round(TPS, 2),
        "Success Rate (%)": round(success_rate, 2),
        "Execution Time (s)": round(execution_time, 2),
        "Consensus Metrics": consensus.performance_metrics,
    }
    try:
        extended_data["DAG Metrics"] = blockchain.get_performance_metrics()
    except Exception:
        pass
    with open("benchmark_results.json", mode="w") as f:
        json.dump(extended_data, f, indent=2)
    print("[EXPORT] 📁 Extended benchmark results saved to benchmark_results.json")

if __name__ == "__main__":
    benchmark()