# 02-logic-engine (PAIR 2 ONLY)

## Strict Rules
- **Stack:** Python, Pandas, Scikit-Learn / IBM Snap ML, hashlib, hmac.
- **Role:** Telemetry simulation, HMAC signing, anomaly detection, deterministic routing.
- **Strict Boundary:** Do NOT touch React. Do NOT start FastAPI servers. Output exported models and rules to `artifacts/`.

## Target Files
- `data_generator.py` (Continuous stream + HMAC edge signing)
- `attack_injector.py` (Spoofed payload generator)
- `train_snap_ml.py` (Random Forest model exportable via PMML/PKL)
- `routing_algorithm.py` (Deterministic graph routing solver)
