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

# Get correctly identified anomalies
anomaly_mask = y_test == 1
X_anomaly = X_test[anomaly_mask]
y_pred_orig = rf.predict(X_anomaly)
correctly_caught = (y_pred_orig == 1).sum()

print(f"=== ADVERSARIAL ROBUSTNESS TEST ===\n")
print(f"Original anomalies caught: {correctly_caught}/{len(X_anomaly)} ({correctly_caught/len(X_anomaly)*100:.1f}%)\n")

# Adversarial perturbation - attacker slightly modifies top features
# to mimic normal traffic statistics
top_features = ['e6b_flow_duration_ms', 'e2c_total_bytes']
normal_means = X_test[y_test==0][top_features].mean()

X_adversarial = X_anomaly.copy()
for feat in top_features:
    if feat in X_adversarial.columns:
        # Attacker shifts anomalous traffic 50% toward normal mean
        X_adversarial[feat] = X_adversarial[feat] + 0.5 * (normal_means[feat] - X_adversarial[feat])

y_pred_adv = rf.predict(X_adversarial)
evaded = (y_pred_adv == 0).sum()
still_caught = (y_pred_adv == 1).sum()

print(f"After adversarial perturbation (50% shift toward normal):")
print(f"Still detected: {still_caught}/{len(X_anomaly)} ({still_caught/len(X_anomaly)*100:.1f}%)")
print(f"Evaded detection: {evaded}/{len(X_anomaly)} ({evaded/len(X_anomaly)*100:.1f}%)")

evasion_rate = evaded/len(X_anomaly)*100

result = {
    "original_detection_rate": round(correctly_caught/len(X_anomaly)*100, 2),
    "perturbed_detection_rate": round(still_caught/len(X_anomaly)*100, 2),
    "evasion_rate": round(evasion_rate, 2),
    "attack_method": "50% feature shift on top-2 importance features toward normal class mean",
    "robustness_verdict": "Model shows vulnerability to feature manipulation" if evasion_rate > 20 else "Model demonstrates reasonable robustness to simple evasion"
}

with open('/home/benny/quantum-resistant-tls-lab/docs/adversarial-robustness.json','w') as f:
    json.dump(result, f, indent=2)

print(f"\nVerdict: {result['robustness_verdict']}")
print("Saved to docs/adversarial-robustness.json")
