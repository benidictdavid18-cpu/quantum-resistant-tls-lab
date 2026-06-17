import subprocess, time, numpy as np, json, os
from scipy import stats

def measure(port, groups, n=500):
    times = []
    for i in range(n):
        env = os.environ.copy()
        env["OPENSSL_CONF"] = "/etc/ssl/openssl-oqs.cnf"
        cmd = ["openssl","s_client","-connect",f"localhost:{port}",
               "-tls1_3","-groups",groups,"-brief"]
        start = time.perf_counter()
        subprocess.run(cmd, env=env, capture_output=True, input=b"", timeout=5)
        times.append((time.perf_counter()-start)*1000)
    return np.array(times)

print("Measuring ML-KEM-768 (n=500)...")
t768 = measure(4434, "X25519MLKEM768")
print("Measuring ML-KEM-1024 (n=500)...")
t1024 = measure(4436, "MLKEM1024")

stat, pvalue = stats.mannwhitneyu(t768, t1024)
distinguishable = pvalue < 0.05

print(f"\nML-KEM-768:  mean={t768.mean():.2f}ms std={t768.std():.2f}ms")
print(f"ML-KEM-1024: mean={t1024.mean():.2f}ms std={t1024.std():.2f}ms")
print(f"Mann-Whitney U p-value: {pvalue:.6f}")
print(f"Statistically distinguishable: {distinguishable}")

result = {
    "mlkem768_mean": round(float(t768.mean()),4),
    "mlkem1024_mean": round(float(t1024.mean()),4),
    "p_value": float(pvalue),
    "distinguishable_via_timing": bool(distinguishable),
    "security_implication": "Attacker observing only encrypted timing can identify PQC security level" if distinguishable else "Timing alone insufficient to fingerprint PQC mode"
}
with open('/home/benny/quantum-resistant-tls-lab/docs/sidechannel-fingerprint.json','w') as f:
    json.dump(result, f, indent=2)
print("\nSaved to docs/sidechannel-fingerprint.json")
