# External Validation - Google Colab

Independent validation performed on Google Colab (separate OS, hardware, 
and Python environment) confirms result stability.

| Metric | Kali Local | Google Colab | Difference |
|---|---|---|---|
| 5-Fold CV ROC-AUC | 0.9815 ± 0.0018 | 0.9812 ± 0.0020 | 0.0003 |
| Test Set ROC-AUC | 0.9847 | 0.9842 | 0.0005 |
| Optimal Threshold Precision | 1.0000 | 1.0000 | 0 |
| Optimal Threshold Recall | 0.8283 | 0.8283 | 0 |

ROC-AUC variance under 0.001 across independent environments confirms 
the Random Forest classifier's discriminative performance is not an 
artifact of the local lab environment.
