# Phase 5 - Benchmarking Results

## Handshake Latency Comparison

| Configuration | Classical Avg | PQC Hybrid Avg | Overhead |
|---|---|---|---|
| Normal Spec (2 core/4GB) | 18.35ms | 31.46ms | +71.4% |
| IoT Simulated (50% CPU) | 16.21ms | 28.57ms | +76.2% |

## Key Findings

| Metric | Value |
|---|---|
| Classical min | 15.22ms |
| Classical max | 25.26ms |
| PQC Hybrid min | 27.43ms |
| PQC Hybrid max | 37.94ms |
| IoT overhead increase | +4.8% vs normal spec |

## Environment
- OS: Kali Linux 6.18.12+kali-amd64
- OpenSSL: 3.6.2
- liboqs: 0.15.0
- Algorithm: X25519 + ML-KEM-768 (NIST FIPS 203)
- Test runs: 10 per configuration

## Conclusion
PQC hybrid handshake introduces 71-76% latency overhead vs classical.
IoT devices with limited CPU show marginally higher overhead (+4.8%).
Both scenarios remain under 40ms — acceptable for most deployments.
Under 100ms threshold for web applications per Google Core Web Vitals.
