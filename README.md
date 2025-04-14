# Thesis Project Summary

**Title:** *Revolutionizing Blockchain Consensus: Scalable, Energy-Efficient, and Fault-Tolerant Algorithms for Next-Generation Distributed Systems*

---

## 🔧 1. Overall Architecture

You’ve designed and implemented a full-stack prototype of a novel **hybrid blockchain consensus system** that combines:

| Layer        | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| **Smart Contract** | A Solidity-based contract (`EnhancedConsensus.sol`) that includes DAG-like structure, validator voting (U-PBFT-style), energy scoring, and leader rotation. |
| **Backend**        | A Python Flask API (`api.py`) that connects the smart contract, machine learning model, and simulation interface. |
| **Consensus Logic**| A simulated DAG + U-PBFT consensus mechanism with selective node participation and trust modeling. |
| **Deployment Tool**| A Hardhat-based local blockchain used for smart contract compilation, testing, and deployment. |

---

## 🧠 2. Key Features Implemented

| Feature                      | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| 🧱 **DAG-based TX Structure**   | Each transaction stores references to parent TXs, forming a DAG-like flow. |
| ⚖ **U-PBFT Voting**           | Transactions require validator approvals (`MIN_APPROVALS`) before commitment. |
| 🔋 **Energy Efficiency**       | Each node is assigned an `energyScore`; low-energy nodes can be excluded.  |
| 🔍 **Reputation Tracking**     | `getReputation()` combines energy and fraud count to assess validator trust. |
| 🔁 **Leader Rotation**         | `rotateLeader()` simulates VRF-based election via `block.prevrandao`.       |
| 📈 **Testing**                | A `load_test.py` script sends batch TXs, simulates fraud, and tracks performance. |
| 🤖 **AI Fraud Detection**     | A trained `fraud_detection_model.pkl` is used to detect and flag malicious behavior. |

---

## 🧪 3. Simulation & Deployment Environment

| Tool | Purpose |
|------|---------|
| **Hardhat** | Simulates a blockchain node locally (`localhost:8545`) |
| **Flask API** | Exposes routes for submitting, approving, and analyzing transactions |
| **Python Scripts** | Used for automated testing and DAG simulations |
| **Smart Contract Deployment** | Managed via `scripts/deploy.js` using Hardhat |

---

## 🧠 4. Research Integration

The implementation directly reflects the concepts proposed in your thesis:
- **Scalability**: DAG structure enables parallel transaction validation.
- **Energy Efficiency**: AI and node profiling reduce unnecessary computation.
- **Fault Tolerance**: PBFT-style voting + ML detection prevents double spending or Sybil attacks.
- **Real-World Use**: Designed for UAV swarms, DeFi, and energy-aware distributed systems.

---

## 🔜 5. Next Steps

| Task | Status |
|------|--------|
| Fix `ethers` injection for deployment | 🔄 In progress |
| Update `api.py` with new endpoints | ⏳ Next step |
| Run full DAG + U-PBFT simulation and benchmark | 🔜 After deploy |
| Document evaluation metrics for thesis | 🔜 Before final report |