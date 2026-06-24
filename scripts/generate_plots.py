import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (confusion_matrix, roc_curve, auc,
    precision_recall_curve, ConfusionMatrixDisplay)
import matplotlib.pyplot as plt

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
y_prob = rf.predict_proba(X_test)[:,1]
y_pred_default = rf.predict(X_test)
y_pred_optimal = (y_prob >= 0.6154).astype(int)

fig, axes = plt.subplots(2, 2, figsize=(14,12))

# Confusion Matrix - default threshold
cm1 = confusion_matrix(y_test, y_pred_default)
ConfusionMatrixDisplay(cm1, display_labels=['Normal','Anomaly']).plot(ax=axes[0,0], cmap='Blues')
axes[0,0].set_title('Confusion Matrix (Default Threshold 0.5)')

# Confusion Matrix - optimal threshold
cm2 = confusion_matrix(y_test, y_pred_optimal)
ConfusionMatrixDisplay(cm2, display_labels=['Normal','Anomaly']).plot(ax=axes[0,1], cmap='Greens')
axes[0,1].set_title('Confusion Matrix (Optimal Threshold 0.6154)')

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
axes[1,0].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
axes[1,0].plot([0,1],[0,1], color='navy', lw=1, linestyle='--')
axes[1,0].set_xlabel('False Positive Rate')
axes[1,0].set_ylabel('True Positive Rate')
axes[1,0].set_title('ROC Curve - Random Forest Classifier')
axes[1,0].legend(loc='lower right')

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_prob)
axes[1,1].plot(recall, precision, color='purple', lw=2)
axes[1,1].set_xlabel('Recall')
axes[1,1].set_ylabel('Precision')
axes[1,1].set_title('Precision-Recall Curve')

plt.tight_layout()
plt.savefig('/home/benny/quantum-resistant-tls-lab/docs/ml-evaluation-plots.png', dpi=150)
print("Saved to docs/ml-evaluation-plots.png")
