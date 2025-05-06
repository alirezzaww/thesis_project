# 🚀 Thesis Project: Revolutionizing Blockchain Consensus

**Title:** *Revolutionizing Blockchain Consensus: Scalable, Energy-Efficient, and Fault-Tolerant Algorithms for Next-Generation Distributed Systems*

## 📚 Summary

This project implements a full-stack prototype of a **hybrid blockchain consensus system** optimized for UAV swarms, DeFi, and energy-aware distributed networks. It combines **DAG-based parallelism**, **U-PBFT fault tolerance**, and **AI-based fraud detection** into a coherent and extensible architecture.

This implementation is based on the user’s thesis work and Q1/Q2 journal research in areas such as:
- Hybrid consensus (DAG + PBFT / U-PBFT)
- Trust management and energy scoring
- Fraud detection using machine learning
- Lightweight blockchain for constrained nodes

---

## 🏗️ Architecture Overview

| Layer               | Component                                          | Description |
|---------------------|----------------------------------------------------|-------------|
| 💡 **Smart Contract** | `EnhancedConsensus.sol`                           | Solidity contract handling DAG txs, voting, energy scoring, and leader rotation |
| 🔧 **Backend API**     | `src/api.py` (Flask app)                          | Provides endpoints for TX submission, DAG visualization, fraud detection |
| 🧠 **Consensus Logic**| `src/consensus/hybrid_consensus.py`               | Simulated DAG + U-PBFT consensus with trust/energy-based node selection |
| ⚙️ **Simulation**      | `src/simulation/load_test.py`                     | Stress testing, fraud simulation, transaction batching |
| 🧪 **Fraud Detection** | `src/ai/fraud_detector.py`, `fraud_detection_model.pkl` | AI model trained on TX patterns to classify fraudulence |

---

## ⚙️ How to Run (Dockerized Setup)

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/thesis_project.git
cd thesis_project
```

2. Build & start using Docker:
```bash
docker compose up --build
```

3. Access the backend:
```bash
curl http://127.0.0.1:5000
```

4. Available endpoints:
- `POST /predict` — classify TX using AI and add to DAG
- `GET /get_blocks` — get DAG block list
- `POST /add_tx` — manually add TX (simulated)
- `GET /health` — system status

---

## 🔬 Research Contributions

Based on journal papers and thesis goals:
- **Hybrid Consensus**: U-PBFT layered on DAG to balance scalability and fault tolerance.
- **Energy-Aware Participation**: Node roles weighted by reputation and energy score.
- **Secure Routing for UAVs**: Inspired by BC-UTSON, BMWSL, and TPDR trust models.
- **AI in Blockchain**: Real-time fraud prediction enhances transaction integrity.
- **Scalability**: DAG allows parallel validation, reduces bottlenecks.

---

## 🧪 Benchmark & Simulation Tools

- `src/simulation/load_test.py`: simulate heavy TX load, inject fraud
- `fraud_detection_model.pkl`: trained with scikit-learn, used for TX classification
- `scripts/deploy.js`: deploy smart contract on Hardhat (localhost:8545)

---

## 🗺️ Project Structure

```
thesis_project/
│
├── src/
│   ├── api.py                     # Main Flask API
│   ├── ai/                        # ML model + fraud detection logic
│   ├── consensus/                 # DAG + U-PBFT implementation
│   ├── simulation/                # Benchmark tools
│   └── utils/                     # Helper functions
│
├── contracts/                     # Solidity contracts
├── scripts/                       # Hardhat deployment scripts
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 📈 Evaluation Metrics (Planned)

| Metric              | Description |
|---------------------|-------------|
| TX Throughput       | Measure of processed transactions/sec |
| Energy Efficiency   | CPU time per TX; participation reduction rate |
| Consensus Latency   | Time to commit a TX |
| Fraud Detection Rate| Precision/recall of ML classification |
| Fault Tolerance     | Recovery rate under node failure/sybil attack |

---

## 🧭 Future Work

- Integrate smart contract deployment from API
- Visualize DAG and validator status in frontend
- Extend ML to detect sybil & selfish mining patterns
- Evaluate on Raspberry Pi swarm

---

## 📣 Contact

For academic collaboration or feedback, contact **Alireza [alirezaerfanianmohrsaz@yahooo.com]**