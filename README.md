# Quantum-Resistant TLS 1.3 Handshake Anomaly Detection

> Build it. Break it. Detect it.

## Project Overview
A complete Post-Quantum Cryptography (PQC) lab implementing NIST FIPS 203 ML-KEM-768 in TLS 1.3, simulating real network attacks, and detecting them using a three-layer hybrid detection system.

**Total Cost: Rs. 0 — 100% Free & Open Source**

---

## Environment
| Component | Version |
|---|---|
| OS | Kali Linux 6.18.12+kali-amd64 |
| OpenSSL | 3.6.2 |
| liboqs | 0.15.0 |
| OQS-Provider | 0.12.0 |
| Python | 3.13.1 |
| Suricata | 8.0.5 |

---

## Architecture
VM1 (Server) 192.168.56.101          VM2 (Attacker) 192.168.56.102

├── Classical TLS 1.3 :4433          ├── Attack 1: Downgrade

├── PQC Hybrid TLS 1.3 :4434         ├── Attack 2: HNDL Capture

└── Expired PQC TLS :4435            ├── Attack 3: Misconfiguration

└── Attack 4: Timing
---

## Phases Completed

### Phase 1 — Environment Setup
- Compiled liboqs 0.15.0 from source
- Built OQS-Provider 0.12.0 integrated with OpenSSL 3.6.2
- Configured both classical and PQC providers simultaneously

### Phase 2 — Implementation
- Generated Classical RSA-4096 certificate
- Generated Post-Quantum ML-DSA-65 certificate (NIST FIPS 204)
- Ran Classical TLS 1.3 server on port 4433
- Ran PQC Hybrid TLS 1.3 server on port 4434 (X25519 + ML-KEM-768)
- Captured handshakes in Wireshark
- Validated ML-KEM-768 against NIST FIPS 203 KAT vectors

### Phase 3 — Attack Simulation
| Attack | Method | Result |
|---|---|---|
| TLS Downgrade | Force P-256 only | Blocked — SSL alert 40 |
| HNDL Capture | Raw message interception | 10,161 bytes captured |
| Misconfiguration | Expired ML-DSA-65 cert | Validation failed |
| Side-Channel Timing | Python benchmark | 47.5% overhead measured |

All attacks executed from VM2 (192.168.56.102) against VM1 (192.168.56.101).

### Phase 4 — SOC Detection
**Layer 1 — Suricata Rules**
- 4 custom rules for PQC attack patterns
- PQC-DOWNGRADE and PQC-BYPASS alerts fired against real pcaps

**Layer 2 — Elastic SIEM**
- Latency anomaly rule triggered at 26.13ms vs 23.04ms threshold
- HIGH severity alert generated

### Phase 5 — Benchmarking
| Scenario | Classical | PQC Hybrid | Overhead |
|---|---|---|---|
| Normal spec (2 core/4GB) | 18.35ms | 31.46ms | +71.4% |
| IoT simulated (50% CPU) | 16.21ms | 28.57ms | +76.2% |
| Network VM2 classical | 22.4ms | — | baseline |

### Phase 6 — ML Anomaly Detection
Dataset: CIC-PQC_OAV v1 (UNB) — 40,010 TLS 1.3 sessions

| Model | Accuracy | ROC-AUC |
|---|---|---|
| Random Forest | 88% | 0.9847 |
| Isolation Forest | 93% | unsupervised |

**Top Detection Features:**
1. `e6b_flow_duration_ms` — handshake latency
2. `e2c_total_bytes` — total bytes transferred
3. `e9_conn_outcome_Success` — connection outcome
4. `e2_server_record_len` — server record length
5. `e1_alg_suite_mlkem768` — algorithm suite

---

## Three-Layer Detection Architecture
---

## Repository Structure
quantum-resistant-tls-lab/

├── configs/openssl-oqs.cnf

├── certs/

├── pcaps/

│   ├── classical-handshake.pcapng

│   ├── hybrid-handshake.pcapng

│   └── hndl-capture.pcapng

├── docs/

│   ├── mlkem-kat-results.txt

│   ├── attack1-downgrade.txt

│   ├── attack2-hndl-messages.txt

│   ├── attack3-misconfiguration.txt

│   ├── attack4-timing-results.json

│   ├── attack1-network-downgrade.txt

│   ├── attack2-network-hndl.txt

│   ├── attack3-network-misconfig.txt

│   ├── attack4-network-timing.txt

│   ├── attack-detection-map.md

│   ├── phase5-benchmark-results.md

│   └── ml-detection-results.json

├── rules/

│   ├── pqc-detection.rules

│   └── elastic-siem-rule.json

├── scripts/

│   ├── timing_benchmark.py

│   └── ml_anomaly_detection.py

└── datasets/

├── ml_features_and_labels.csv

└── scenario_manifest.csv


---

## Key Findings
- PQC Hybrid handshake introduces **71-76% latency overhead** vs classical
- Downgrade attacks **blocked** by ML-KEM group enforcement
- ML model achieves **ROC-AUC 0.9847** on CIC-PQC_OAV v1 dataset
- Three-layer detection catches **94% of anomalies** with recall

---

## Novel Contribution
Most PQC research only benchmarks performance. This project:
1. **Implements** ML-KEM-768 (NIST FIPS 203) in real TLS 1.3
2. **Attacks** it from a real network using 4 attack vectors
3. **Detects** attacks using Suricata + Random Forest + Isolation Forest

---

## Standards Referenced
- NIST FIPS 203 — ML-KEM (Kyber)
- NIST FIPS 204 — ML-DSA (Dilithium)
- IETF draft-ietf-tls-hybrid-design
- CIC-PQC_OAV v1 Dataset (UNB, 2025)

---

## Author
Benidict David
GitHub: benidictdavid18-cpu
