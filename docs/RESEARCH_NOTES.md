# EcoRevive Research Notes
Research question: How can product lifecycle information, ML predictions, logistics optimization, and verifiable events be combined to improve e-waste reverse-logistics decisions?

Hypotheses:
- H1: Product condition and lifecycle features improve return prediction over age/category-only baselines.
- H2: Priority-aware routing reduces distance or estimated cost against a declared baseline under the same constraints.
- H3: Hash verification detects altered records and invalid links in the application ledger.

Metrics:
- Return classifier: PR-AUC, ROC-AUC, precision, recall, F1, calibration.
- Recovery pathway: macro-F1, per-class recall, confusion matrix.
- Value regression: MAE, RMSE.
- Routing: distance, estimated cost, stop completion, feasibility.
- Audit: tamper detection, event recording latency.

The seed records and generated model-training data are synthetic. Results only validate software and simulated scenarios; they do not establish real-world accuracy or environmental savings. Document provenance and avoid future-data leakage.
