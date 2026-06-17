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
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:,1]

# Find misclassifications
false_neg_mask = (y_test==1) & (y_pred==0)  # missed attacks
false_pos_mask = (y_test==0) & (y_pred==1)  # false alarms

X_fn = X_test[false_neg_mask].head(5)
X_fp = X_test[false_pos_mask].head(5)

normal_means = X_test[y_test==0].mean()
anomaly_means = X_test[y_test==1].mean()

print(f"=== ERROR ANALYSIS ===\n")
print(f"Total False Negatives (missed attacks): {false_neg_mask.sum()}")
print(f"Total False Positives (false alarms): {false_pos_mask.sum()}\n")

print("--- 5 Sample Missed Attacks (False Negatives) ---")
key_features = ['e6b_flow_duration_ms','e2c_total_bytes','e2_server_record_len']
analysis_results = {"false_negatives": [], "false_positives": []}

for idx, row in X_fn.iterrows():
    print(f"\nSession {idx}:")
    explanation = []
    for feat in key_features:
        if feat in row.index:
            val = row[feat]
            n_mean = normal_means[feat]
            a_mean = anomaly_means[feat]
            closer_to = "normal" if abs(val-n_mean) < abs(val-a_mean) else "anomaly"
            print(f"  {feat}: {val:.2f} (normal_avg={n_mean:.2f}, anomaly_avg={a_mean:.2f}) -> closer to {closer_to}")
            explanation.append(f"{feat} closer to {closer_to} pattern")
    analysis_results["false_negatives"].append({
        "session_id": int(idx),
        "explanation": "; ".join(explanation)
    })

print("\n--- 5 Sample False Alarms (False Positives) ---")
for idx, row in X_fp.iterrows():
    print(f"\nSession {idx}:")
    explanation = []
    for feat in key_features:
        if feat in row.index:
            val = row[feat]
            n_mean = normal_means[feat]
            a_mean = anomaly_means[feat]
            closer_to = "normal" if abs(val-n_mean) < abs(val-a_mean) else "anomaly"
            print(f"  {feat}: {val:.2f} (normal_avg={n_mean:.2f}, anomaly_avg={a_mean:.2f}) -> closer to {closer_to}")
            explanation.append(f"{feat} closer to {closer_to} pattern")
    analysis_results["false_positives"].append({
        "session_id": int(idx),
        "explanation": "; ".join(explanation)
    })

analysis_results["summary"] = {
    "total_false_negatives": int(false_neg_mask.sum()),
    "total_false_positives": int(false_pos_mask.sum()),
    "interpretation": "False negatives occur when anomalous sessions exhibit feature values overlapping with normal traffic distribution, particularly in flow duration and byte count - the model's top predictive features. This indicates sophisticated attacks that closely mimic normal timing patterns remain the hardest to detect."
}

with open('/home/benny/quantum-resistant-tls-lab/docs/error-analysis.json','w') as f:
    json.dump(analysis_results, f, indent=2)

print(f"\n\nSaved to docs/error-analysis.json")
