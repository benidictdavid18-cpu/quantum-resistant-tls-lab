import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import json
import os

print("=== PQC TLS 1.3 Anomaly Detection - ML Layer ===\n")

# Load dataset
df = pd.read_csv('/home/benny/quantum-resistant-tls-lab/datasets/ml_features_and_labels.csv')
print(f"Dataset: {df.shape[0]} sessions, {df.shape[1]} features")

# Drop non-feature columns
drop_cols = ['split', 'taxonomy', 'ID']
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# Convert booleans to int
bool_cols = df.select_dtypes(include='bool').columns
df[bool_cols] = df[bool_cols].astype(int)

# Separate features and label
X = df.drop(columns=['label'])
y = df['label']

print(f"Normal sessions: {(y==0).sum()}")
print(f"Anomalous sessions: {(y==1).sum()}")
print(f"Features used: {X.shape[1]}\n")

# Check missing values
missing = X.isnull().sum().sum()
print(f"Missing values: {missing}")
if missing > 0:
    X = X.fillna(X.median())

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training: {len(X_train)} | Testing: {len(X_test)}\n")

# Layer 1 - Random Forest Classifier
print("--- Layer 1: Random Forest Classifier ---")
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=2,
    class_weight='balanced'
)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:,1]

print(classification_report(y_test, y_pred,
    target_names=['Normal','Anomaly']))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}\n")

# Layer 2 - Isolation Forest (unsupervised)
print("--- Layer 2: Isolation Forest (Unsupervised) ---")
iso = IsolationForest(
    contamination=0.125,
    random_state=42,
    n_jobs=2
)
iso.fit(X_train)
iso_pred = iso.predict(X_test)
iso_pred = (iso_pred == -1).astype(int)

print(classification_report(y_test, iso_pred,
    target_names=['Normal','Anomaly']))

# Feature importance
print("--- Top 10 Most Important Features ---")
feat_imp = pd.Series(rf.feature_importances_, index=X.columns)
top10 = feat_imp.nlargest(10)
for feat, imp in top10.items():
    print(f"  {feat}: {imp:.4f}")

# Save results
results = {
    "model": "RandomForest + IsolationForest",
    "dataset": "CIC-PQC_OAV v1",
    "total_sessions": len(df),
    "normal": int((y==0).sum()),
    "anomalous": int((y==1).sum()),
    "rf_roc_auc": round(roc_auc_score(y_test, y_prob), 4),
    "top_features": top10.index.tolist()
}

output_path = '/home/benny/quantum-resistant-tls-lab/docs/ml-detection-results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to docs/ml-detection-results.json")
print("\n=== ML Detection Layer Complete ===")
