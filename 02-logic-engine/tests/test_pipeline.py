import os
import json
import joblib
import pandas as pd
import numpy as np

def test_dataset():
    """Verifies CSV existence, dimensions, columns, value integrity, and anomaly distribution."""
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'synthetic_hospital_data_10k.csv')
    assert os.path.exists(csv_path), f"Dataset missing at {csv_path}"

    df = pd.read_csv(csv_path)
    print(f"[TEST 1: Dataset Size] Found {len(df)} rows (Expected: 10,000)")
    assert len(df) == 10000, f"Expected 10,000 rows, got {len(df)}"

    expected_cols = [
        "timestamp", "sensor_location", "grid_voltage",
        "water_pressure", "flood_index", "route_congestion", "is_anomaly"
    ]
    print(f"[TEST 2: Column Schema] Columns: {list(df.columns)}")
    assert list(df.columns) == expected_cols, f"Column mismatch: {list(df.columns)} != {expected_cols}"

    print("[TEST 3: Null / Inf Integrity] Checking for missing or infinite values...")
    assert df.isnull().sum().sum() == 0, "Dataset contains null values"
    for col in ["grid_voltage", "water_pressure", "flood_index", "route_congestion"]:
        assert np.isfinite(df[col]).all(), f"Column {col} contains non-finite values"
    print("  -> Zero null or infinite values found. Clean.")

    counts = df["is_anomaly"].value_counts().to_dict()
    print(f"[TEST 4: Anomaly Distribution] Nominal: {counts.get(0, 0)}, Anomalous: {counts.get(1, 0)}")
    assert counts.get(0, 0) > 9000, "Too few nominal samples"
    assert counts.get(1, 0) > 100, "Too few anomaly samples"

def test_model_loading_and_inference():
    """Verifies that the exported artifact loads with joblib and produces predictions on sample data."""
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'anomaly_model.pkl')
    assert os.path.exists(model_path), f"Model artifact missing at {model_path}"

    print(f"[TEST 5: Model Artifact Loading] Loading {model_path} via joblib...")
    model = joblib.load(model_path)
    assert model is not None, "Model failed to load"
    print(f"  -> Model class: {type(model).__name__}")

    features = ['grid_voltage', 'flood_index', 'route_congestion']

    # Test Sample 1: Nominal readings
    sample_nominal = pd.DataFrame([[220.5, 0.05, 35]], columns=features)
    pred_nominal = model.predict(sample_nominal)[0]

    # Test Sample 2: Catastrophic Flood Anomaly
    sample_flood = pd.DataFrame([[205.0, 0.95, 95]], columns=features)
    pred_flood = model.predict(sample_flood)[0]

    # Test Sample 3: Power Grid Blackout Anomaly
    sample_blackout = pd.DataFrame([[45.0, 0.10, 85]], columns=features)
    pred_blackout = model.predict(sample_blackout)[0]

    print("[TEST 6: Sample Inference Output]")
    print(f"  Nominal sample prediction: {pred_nominal} (Expected inlier: +1)")
    print(f"  Flood anomaly prediction: {pred_flood} (Expected outlier: -1)")
    print(f"  Blackout anomaly prediction: {pred_blackout} (Expected outlier: -1)")

    assert pred_nominal == 1, f"Expected +1 for nominal inlier, got {pred_nominal}"
    assert pred_flood == -1, f"Expected -1 for flood outlier, got {pred_flood}"
    assert pred_blackout == -1, f"Expected -1 for blackout outlier, got {pred_blackout}"
    print("  -> All sample inferences match Isolation Forest convention (+1 normal, -1 anomaly).")

def test_metadata():
    """Verifies model metadata file and feature ordering documentation."""
    meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'model_metadata.json')
    assert os.path.exists(meta_path), f"Metadata missing at {meta_path}"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    print(f"[TEST 7: Metadata & Feature Order] Features: {meta.get('features')}")
    assert meta.get('features') == ['grid_voltage', 'flood_index', 'route_congestion']
    assert "backend_compatibility_note" in meta

if __name__ == "__main__":
    print("=" * 60)
    print("PROJECT SYN — PAIR 2 PIPELINE TEST SUITE")
    print("=" * 60)
    test_dataset()
    test_model_loading_and_inference()
    test_metadata()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY (7/7)")
    print("=" * 60)
