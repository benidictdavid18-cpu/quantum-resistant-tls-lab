# Attack vs Detection Map

| Attack | Tool | Suricata Rule | SID | Result |
|--------|------|---------------|-----|--------|
| PQC Downgrade | Custom OpenSSL client | PQC-DOWNGRADE | 1000001 | DETECTED |
| HNDL Capture | Wireshark pcap | PQC-BYPASS | 1000002 | DETECTED |
| Misconfiguration | Expired ML-DSA-65 cert | PQC-MISCONFIGURATION | 1000003 | DETECTED |
| Side-Channel Timing | Python timing script | PQC-TIMING | 1000004 | MONITORED |

## Key Finding
All 4 attack scenarios produce detectable network signatures.
Suricata rules validated against live attack captures.
