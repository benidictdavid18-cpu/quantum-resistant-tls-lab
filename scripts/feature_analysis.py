import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import json

df = pd.read_csv('/home/benny/quantum-resistant-tls-lab/datasets/ml_features_and_labels.csv')
df = df.drop(columns=['split','taxonomy','ID'], errors='ignore')
bool_cols = df.select_dtypes(include='bool').columns
df[bool_cols] = df[bool_cols].astype(int)
df = df.fillna(df.median(numeric_only=True))

X = df.drop(columns=['label'])
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=100, max_depth=10,
    class_weight='balanced', random_state=42, n_jobs=2)
rf.fit(X_train, y_train)

feat_imp = pd.Series(rf.feature_importances_, index=X.columns)
top15 = feat_imp.nlargest(15)

# Cryptographic justification for each feature
justifications = {
    "e6b_flow_duration_ms": "PQC key encapsulation adds measurable latency. ML-KEM-768 key generation and encapsulation takes longer than X25519 elliptic curve operations. Anomalous duration indicates algorithm mismatch or downgrade.",
    "e2c_total_bytes": "ML-KEM-768 public key is 1184 bytes vs X25519 32 bytes. PQC handshakes transfer significantly more data. Deviation from expected size indicates misconfiguration or stripping attack.",
    "e9_conn_outcome_Success": "Failed connections on PQC port indicate active attacks. Downgrade attempts and misconfigured clients produce connection failures not seen in normal PQC traffic.",
    "e2_server_record_len": "ML-DSA-65 certificates are 7456 bytes vs RSA-4096 1830 bytes. Server record length directly reflects certificate algorithm. Classical-sized records on PQC port indicate downgrade.",
    "e2_client_record_len": "ClientHello with PQC key share is 1400+ bytes. Classical ClientHello is under 400 bytes. Small client records on PQC port indicate missing ML-KEM key share — downgrade indicator.",
    "e6_time_char": "Time characteristics of PQC handshake follow predictable pattern. Deviations indicate timing attacks or side-channel probing.",
    "e2_client_size": "ML-KEM-768 key share in ClientHello adds 1088 bytes. Absence of this size increase on PQC port is direct evidence of key share stripping.",
    "e1_alg_suite_mlkem768": "Algorithm suite indicator. Absence of ML-KEM-768 on hybrid port directly identifies downgrade or misconfiguration.",
    "e1_alg_suite_mlkem1024": "Higher security PQC mode. Presence on wrong port indicates misconfiguration.",
    "e1_alg_suite_x25519": "Classical algorithm indicator. Presence alone on hybrid port indicates successful downgrade attack."
}

print("=== FEATURE IMPORTANCE WITH CRYPTOGRAPHIC JUSTIFICATION ===\n")
results = []
for feat, imp in top15.items():
    justification = justifications.get(feat, "Statistical correlation with anomaly class in CIC-PQC_OAV v1 dataset.")
    print(f"Feature: {feat}")
    print(f"Importance: {imp:.4f} ({imp*100:.1f}%)")
    print(f"Why: {justification}")
    print()
    results.append({
        "feature": feat,
        "importance": round(float(imp), 4),
        "percentage": round(float(imp)*100, 1),
        "cryptographic_justification": justification
    })

with open('/home/benny/quantum-resistant-tls-lab/docs/feature-analysis.json','w') as f:
    json.dump(results, f, indent=2)

print("Saved to docs/feature-analysis.json")
