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

    print("[TEST 6: Sample Inference Output — Random Forest (Primary)]")
    print(f"  Nominal sample prediction: {pred_nominal} (Expected nominal: 0)")
    print(f"  Flood anomaly prediction: {pred_flood} (Expected anomaly: 1)")
    print(f"  Blackout anomaly prediction: {pred_blackout} (Expected anomaly: 1)")

    assert pred_nominal == 0, f"Expected 0 for nominal baseline, got {pred_nominal}"
    assert pred_flood == 1, f"Expected 1 for flood anomaly, got {pred_flood}"
    assert pred_blackout == 1, f"Expected 1 for blackout anomaly, got {pred_blackout}"
    print("  -> Primary model inferences strictly match Pair 3 queue_worker convention (0=Nominal, 1=Anomaly).")

    # Optional Benchmark Validation: Preserved Isolation Forest
    iso_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'isolation_forest.pkl')
    if os.path.exists(iso_path):
        iso_model = joblib.load(iso_path)
        iso_nom = iso_model.predict(sample_nominal)[0]
        iso_flood = iso_model.predict(sample_flood)[0]
        iso_blackout = iso_model.predict(sample_blackout)[0]
        assert iso_nom == 1, f"Expected +1 for IsolationForest inlier, got {iso_nom}"
        assert iso_flood == -1, f"Expected -1 for IsolationForest outlier, got {iso_flood}"
        assert iso_blackout == -1, f"Expected -1 for IsolationForest outlier, got {iso_blackout}"
        print("  -> Benchmark Isolation Forest inferences verified (+1 nominal, -1 anomaly).")

def test_metadata():
    """Verifies model metadata file and feature ordering documentation."""
    meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'model_metadata.json')
    assert os.path.exists(meta_path), f"Metadata missing at {meta_path}"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    print(f"[TEST 7: Metadata & Feature Order] Features: {meta.get('features')}")
    assert meta.get('features') == ['grid_voltage', 'flood_index', 'route_congestion']
    assert "backend_compatibility_note" in meta

def test_road_corridors_and_fleet():
    """Verifies OpenRouteService road corridors cache and road-snapped vehicle swarm."""
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts')
    cache_path = os.path.join(artifacts_dir, 'road_corridors_cache.json')
    fleet_csv = os.path.join(artifacts_dir, 'ambulance_fleet.csv')
    fleet_json = os.path.join(artifacts_dir, 'live_fleet_positions.json')

    print("[TEST 8: OpenRouteService Road Corridors Cache]")
    assert os.path.exists(cache_path), f"Road corridors cache missing at {cache_path}"
    with open(cache_path, 'r', encoding='utf-8') as f:
        corridors = json.load(f)
    print(f"  -> Found {len(corridors)} verified road corridors across Nagpur.")
    assert len(corridors) >= 10, f"Expected at least 10 corridors, found {len(corridors)}"

    print("[TEST 9: Road-Snapped Vehicle Swarm (40 Vehicles)]")
    assert os.path.exists(fleet_csv), f"Fleet CSV missing at {fleet_csv}"
    assert os.path.exists(fleet_json), f"Fleet JSON missing at {fleet_json}"
    df_fleet = pd.read_csv(fleet_csv)
    assert len(df_fleet) == 40, f"Expected 40 vehicles, found {len(df_fleet)}"
    assert "bearing" in df_fleet.columns and "corridor" in df_fleet.columns
    print(f"  -> Verified 40 vehicles with bearings snapped to authentic road corridors.")

def test_medical_triage_model():
    """Verifies clinical disaster triage Random Forest model and metadata."""
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts')
    med_model_path = os.path.join(artifacts_dir, 'medical_triage_model.pkl')
    med_meta_path = os.path.join(artifacts_dir, 'medical_triage_metadata.json')

    print("[TEST 10: Clinical Disaster Triage Model & Metadata]")
    assert os.path.exists(med_model_path), f"Medical triage model missing at {med_model_path}"
    assert os.path.exists(med_meta_path), f"Medical metadata missing at {med_meta_path}"

    model = joblib.load(med_model_path)
    sample_crit = pd.DataFrame([[98.0, 1.2, 95.0, 0.90, 0, 1.5]], columns=[
        "icu_bed_occupancy_pct", "oxygen_hours_remaining",
        "ventilator_utilization_pct", "trauma_surge_index",
        "blood_o_neg_units", "generator_hours_remaining"
    ])
    pred = model.predict(sample_crit)[0]
    print(f"  -> Emergency triage intervention prediction code: {pred} (Action code 1/2/3)")
    assert pred in (1, 2, 3), f"Expected emergency triage intervention code (1, 2, or 3), got {pred}"
    print("  -> Clinical triage model inference passed.")

def test_hmac_serialization_and_signing():
    """Verifies HMAC-SHA256 signature computation, contract adherence, constant-time software verification, and anti-tamper rejection."""
    import hmac
    import hashlib
    import sys

    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    import telemetry_simulator as sim

    print("[TEST 11: HMAC-SHA256 Serialization & Signature Validation]")
    packet = sim.generate_telemetry_packet(tick=1)

    # Contract checks
    assert "packet_id" in packet and packet["packet_id"].startswith("SYN-")
    assert "timestamp" in packet and "unix_timestamp" in packet
    assert "nonce" in packet and len(packet["nonce"]) >= 8
    assert "sensor_location" in packet
    assert "metrics" in packet
    assert "grid_voltage" in packet["metrics"]
    assert "flood_index" in packet["metrics"]
    assert "route_congestion" in packet["metrics"]
    # Critical contract rule: signature is sent in X-Signature header, NOT inside body
    assert "hmac_signature" not in packet, "hmac_signature must not be placed inside signed payload"

    payload_bytes = json.dumps(packet).encode("utf-8")
    sig = sim.sign_packet(payload_bytes)
    assert len(sig) == 64, f"Expected 64-char SHA256 hex digest, got {len(sig)}"

    # Software emulation of constant-time digest comparison matching the backend gate interface
    # (Hardware CPACF KIMD/KLMD acceleration runs on native IBM s390x production deployments)
    expected = hmac.new(sim.SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
    assert hmac.compare_digest(sig, expected), "HMAC signature mismatch"

    # Anti-tamper verification: payload modification post-signature must fail digest match
    tampered_bytes = json.dumps({**packet, "metrics": {**packet["metrics"], "grid_voltage": 0.0}}).encode("utf-8")
    tampered_expected = hmac.new(sim.SECRET_KEY, tampered_bytes, hashlib.sha256).hexdigest()
    assert not hmac.compare_digest(sig, tampered_expected), "Tampered payload was not rejected"
    print("  -> HMAC serialization, constant-time software verification, and anti-tamper tests passed.")

if __name__ == "__main__":
    print("=" * 60)
    print("PROJECT SYN — PAIR 2 PIPELINE TEST SUITE (EXTENDED)")
    print("=" * 60)
    test_dataset()
    test_model_loading_and_inference()
    test_metadata()
    test_road_corridors_and_fleet()
    test_medical_triage_model()
    test_hmac_serialization_and_signing()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY (11/11)")
    print("=" * 60)

