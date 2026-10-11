import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
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

    # Train Isolation Forest (Pillar 2A: Anomaly Detection)
    print("\n--- Training Isolation Forest Model ---")
    contamination_rate = float(y_train.mean())  # ~0.04 empirical anomaly rate
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination_rate,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train)

    # Scikit-learn Isolation Forest outputs: -1 for outlier/anomaly, +1 for inlier/normal
    raw_preds_test = model.predict(X_test)
    y_pred_binary = np.where(raw_preds_test == -1, 1, 0)

    print("Isolation Forest Test Evaluation (0=Nominal, 1=Anomaly):")
    print(classification_report(y_test, y_pred_binary, target_names=["Nominal", "Anomaly"], digits=4))

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred_binary)),
        "precision": float(precision_score(y_test, y_pred_binary, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred_binary, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred_binary, zero_division=0))
    }

    # Export Primary Model Artifact
    model_path = os.path.join(artifacts_dir, 'anomaly_model.pkl')
    print(f"\nExporting model to {model_path}...")
    joblib.dump(model, model_path)

    # Export Metadata for Backend Handoff
    metadata_path = os.path.join(artifacts_dir, 'model_metadata.json')
    metadata = {
        "model_type": "IsolationForest",
        "library": "scikit-learn",
        "features": features,
        "feature_order": features,
        "n_estimators": 100,
        "contamination": contamination_rate,
        "output_convention": {
            "sklearn_raw_predict": {"+1": "nominal (inlier)", "-1": "anomaly (outlier)"},
            "binary_mapped": {"0": "nominal", "1": "anomaly"}
        },
        "backend_compatibility_note": (
            "Pair 3's queue_worker.py checks `if prediction[0] == 1: is_anomaly = True`. "
            "Because scikit-learn IsolationForest returns +1 for inliers (nominal) and -1 for outliers (anomaly), "
            "Pair 3 should update inference check to `if prediction[0] == -1:` or map `prediction = np.where(prediction == -1, 1, 0)`."
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
