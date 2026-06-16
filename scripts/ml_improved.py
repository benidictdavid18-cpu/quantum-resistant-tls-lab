import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (classification_report, roc_auc_score,
    precision_recall_curve, average_precision_score)
from sklearn.preprocessing import label_binarize
import json

print("=== Improved ML Detection - K-Fold + PR Curve ===\n")

df = pd.read_csv('/home/benny/quantum-resistant-tls-lab/datasets/ml_features_and_labels.csv')
df = df.drop(columns=['split','taxonomy','ID'], errors='ignore')
bool_cols = df.select_dtypes(include='bool').columns
df[bool_cols] = df[bool_cols].astype(int)
df = df.fillna(df.median(numeric_only=True))

X = df.drop(columns=['label'])
y = df['label']

print(f"Dataset: {len(df)} sessions | Features: {X.shape[1]}")
print(f"Normal: {(y==0).sum()} | Anomalous: {(y==1).sum()}\n")

# 5-Fold Cross Validation
rf = RandomForestClassifier(
    n_estimators=100, max_depth=10,
    class_weight='balanced', random_state=42, n_jobs=2)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = ['accuracy','precision_macro','recall_macro',
           'f1_macro','roc_auc']

print("Running 5-Fold Cross Validation...")
cv_results = cross_validate(rf, X, y, cv=cv,
    scoring=scoring, return_train_score=False)

print("\n=== 5-FOLD CV RESULTS ===")
for metric in scoring:
    key = f'test_{metric}'
    scores = cv_results[key]
    print(f"{metric:20s}: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")

# Final model on full data for PR curve
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

rf.fit(X_train, y_train)
y_prob = rf.predict_proba(X_test)[:,1]
y_pred = rf.predict(X_test)

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(y_test, y_pred,
    target_names=['Normal','Anomaly']))

# Precision-Recall
precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
ap = average_precision_score(y_test, y_prob)
print(f"Average Precision Score: {ap:.4f}")
print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")

# Find optimal threshold
f1_scores = 2*precision*recall/(precision+recall+1e-8)
optimal_idx = np.argmax(f1_scores)
optimal_threshold = thresholds[optimal_idx] if optimal_idx < len(thresholds) else 0.5
print(f"Optimal Threshold: {optimal_threshold:.4f}")
print(f"At optimal - Precision: {precision[optimal_idx]:.4f} Recall: {recall[optimal_idx]:.4f}")

# Apply optimal threshold
y_pred_optimal = (y_prob >= optimal_threshold).astype(int)
print("\n=== WITH OPTIMAL THRESHOLD ===")
print(classification_report(y_test, y_pred_optimal,
    target_names=['Normal','Anomaly']))

# Save results
results = {
    "cv_folds": 5,
    "cv_roc_auc_mean": round(cv_results['test_roc_auc'].mean(), 4),
    "cv_roc_auc_std": round(cv_results['test_roc_auc'].std()*2, 4),
    "cv_f1_mean": round(cv_results['test_f1_macro'].mean(), 4),
    "average_precision": round(float(ap), 4),
    "optimal_threshold": round(float(optimal_threshold), 4),
    "optimal_precision": round(float(precision[optimal_idx]), 4),
    "optimal_recall": round(float(recall[optimal_idx]), 4)
}

with open('/home/benny/quantum-resistant-tls-lab/docs/ml-improved-results.json','w') as f:
    json.dump(results, f, indent=2)

print("\nSaved to docs/ml-improved-results.json")
