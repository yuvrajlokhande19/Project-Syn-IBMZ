import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

def train_model():
    """
    Trains a lightweight Isolation Forest anomaly detection model on synthetic hospital telemetry,
    evaluates performance on a held-out test partition, and exports artifacts.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, '..', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)

    data_path = os.path.join(artifacts_dir, 'synthetic_hospital_data_10k.csv')
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Running generator first...")
        from generate_dataset import generate_10k_dataset
        generate_10k_dataset(data_path)

    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

    # Features strictly conforming to the Canonical Project Syn contract & Mainframe queue_worker
    features = ['grid_voltage', 'flood_index', 'route_congestion']
    X = df[features]
    y = df['is_anomaly']

    print(f"Feature matrix shape: {X.shape}, Class distribution: {y.value_counts().to_dict()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # -------------------------------------------------------------
    # 1. Train Primary Model: Random Forest Classifier (Pillar 2A)
    # Compatible with Pair 3's queue_worker.py: if prediction[0] == 1: is_anomaly = True
    # -------------------------------------------------------------
    print("\n--- Training Primary Random Forest Classifier ---")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    y_pred_rf = rf_model.predict(X_test)
    print("Random Forest Test Evaluation (0=Nominal, 1=Anomaly):")
    print(classification_report(y_test, y_pred_rf, target_names=["Nominal", "Anomaly"], digits=4))

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred_rf)),
        "precision": float(precision_score(y_test, y_pred_rf, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred_rf, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred_rf, zero_division=0))
    }

    # -------------------------------------------------------------
    # 2. Train Benchmark Model: Isolation Forest
    # -------------------------------------------------------------
    print("\n--- Training Benchmark Isolation Forest Model ---")
    contamination_rate = float(y_train.mean())  # ~0.04 empirical anomaly rate
    iso_model = IsolationForest(
        n_estimators=100,
        contamination=contamination_rate,
        random_state=42,
        n_jobs=-1
    )
    iso_model.fit(X_train)

    # -------------------------------------------------------------
    # 3. Export Model Artifacts
    # -------------------------------------------------------------
    # Primary artifact loaded by 03-mainframe-core/queue_worker.py
    primary_model_path = os.path.join(artifacts_dir, 'anomaly_model.pkl')
    iso_model_path = os.path.join(artifacts_dir, 'isolation_forest.pkl')
    print(f"\nExporting primary Random Forest model to: {primary_model_path}")
    joblib.dump(rf_model, primary_model_path)
    print(f"Exporting benchmark Isolation Forest model to: {iso_model_path}")
    joblib.dump(iso_model, iso_model_path)

    # Export Metadata for Backend Handoff
    metadata_path = os.path.join(artifacts_dir, 'model_metadata.json')
    metadata = {
        "model_type": "RandomForestClassifier",
        "library": "scikit-learn",
        "features": features,
        "feature_order": features,
        "n_estimators": 100,
        "random_state": 42,
        "output_convention": {
            "raw_predict": {"0": "nominal", "1": "anomaly"}
        },
        "backend_compatibility_note": (
            "Directly compatible with Pair 3's queue_worker.py check: "
            "`if prediction[0] == 1: is_anomaly = True`. "
            "Outputs 0 for nominal sensor vectors and 1 for infrastructure anomalies."
        ),
        "evaluation_metrics": metrics
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Exported metadata to: {metadata_path}")
    print("Model training, evaluation, and export completed successfully.")
    return metrics

if __name__ == "__main__":
    train_model()
