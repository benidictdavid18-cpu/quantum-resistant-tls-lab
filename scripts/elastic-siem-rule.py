import json
import re
from datetime import datetime

# Elastic SIEM Detection Rule Definition
elastic_rule = {
    "rule": {
        "name": "PQC Handshake Latency Anomaly",
        "description": "Detects abnormal TLS handshake latency indicating PQC downgrade or timing attack",
        "severity": "high",
        "risk_score": 73,
        "type": "threshold",
        "language": "kuery",
        "query": 'tls.version:"TLSv1.3" AND destination.port:(4433 OR 4434) AND event.duration > 20000000',
        "threshold": {
            "field": "destination.port",
            "value": 5
        },
        "tags": ["PQC", "TLS", "Quantum", "NIST-FIPS-203"],
        "references": [
            "https://csrc.nist.gov/publications/detail/fips/203/final",
            "https://datatracker.ietf.org/doc/draft-ietf-tls-hybrid-design"
        ],
        "mitre_attack": ["T1040", "T1557"]
    }
}

# Simulate log analysis against timing results
print("=== ELASTIC SIEM RULE SIMULATION ===\n")

# Load timing results
with open('/home/benny/quantum-resistant-tls-lab/docs/attack4-timing-results.json') as f:
    timing_data = json.load(f)

print("Analyzing handshake timing data...\n")

baseline = timing_data['Classical_X25519']['avg']
pqc_avg = timing_data['Hybrid_X25519_MLKEM768']['avg']
threshold_ms = baseline * 1.3  # 30% above baseline = anomaly

print(f"Baseline (Classical):     {baseline}ms")
print(f"PQC Hybrid Average:       {pqc_avg}ms")
print(f"Anomaly Threshold (130%): {threshold_ms:.2f}ms")
print(f"PQC Overhead:             {((pqc_avg-baseline)/baseline*100):.1f}%\n")

# Simulate alert
if pqc_avg > threshold_ms:
    alert = {
        "timestamp": datetime.now().isoformat(),
        "rule_name": "PQC Handshake Latency Anomaly",
        "severity": "HIGH",
        "finding": f"PQC handshake {pqc_avg}ms exceeds threshold {threshold_ms:.2f}ms",
        "recommendation": "Verify PQC hybrid configuration on port 4434",
        "mitre": "T1040 - Network Sniffing",
        "action": "ALERT"
    }
    print(">>> ELASTIC SIEM ALERT TRIGGERED <<<")
    print(json.dumps(alert, indent=2))
else:
    print("No anomaly detected")

# Save rule and findings
output = {
    "elastic_rule": elastic_rule,
    "simulation_results": {
        "baseline_ms": baseline,
        "pqc_avg_ms": pqc_avg,
        "threshold_ms": round(threshold_ms, 2),
        "overhead_percent": round((pqc_avg-baseline)/baseline*100, 1),
        "alert_triggered": pqc_avg > threshold_ms
    }
}

with open('/home/benny/quantum-resistant-tls-lab/rules/elastic-siem-rule.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nElastic SIEM rule saved to rules/elastic-siem-rule.json")
