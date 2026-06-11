import subprocess
import time
import os
import json

results = {}
configs = {
    "Classical_X25519": {
        "port": "4433",
        "groups": "P-256",
        "conf": None
    },
    "Hybrid_X25519_MLKEM768": {
        "port": "4434",
        "groups": "X25519MLKEM768",
        "conf": "/etc/ssl/openssl-oqs.cnf"
    }
}

for name, config in configs.items():
    times = []
    print(f"\nTesting {name}...")
    for i in range(10):
        env = os.environ.copy()
        if config["conf"]:
            env["OPENSSL_CONF"] = config["conf"]
        cmd = [
            "openssl", "s_client",
            "-connect", f"localhost:{config['port']}",
            "-tls1_3",
            "-brief"
        ]
        start = time.perf_counter()
        subprocess.run(cmd, env=env,
            capture_output=True,
            input=b"",
            timeout=5)
        end = time.perf_counter()
        elapsed = (end - start) * 1000
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.2f}ms")

    results[name] = {
        "min": round(min(times), 2),
        "max": round(max(times), 2),
        "avg": round(sum(times)/len(times), 2),
        "all": times
    }

print("\n=== TIMING RESULTS ===")
for name, r in results.items():
    print(f"{name}: avg={r['avg']}ms min={r['min']}ms max={r['max']}ms")

with open(os.path.expanduser(
    "~/quantum-resistant-tls-lab/docs/attack4-timing-results.json"), "w") as f:
    json.dump(results, f, indent=2)

print("\nResults saved to docs/attack4-timing-results.json")
