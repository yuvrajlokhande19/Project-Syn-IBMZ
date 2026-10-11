import os
import json
import random
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def generate_medical_dataset(csv_path: str, n_samples: int = 5000):
    """
    Generates synthetic medical hospital telemetry vectors for critical care disaster triage.
    Features:
    - icu_bed_occupancy_pct: 40% to 100%
    - oxygen_hours_remaining: 0.5 to 72.0 hours
    - ventilator_utilization_pct: 30% to 100%
    - trauma_surge_index: 0.0 (quiet) to 1.0 (mass casualty incident)
    - blood_o_neg_units: 0 to 120 units
    - generator_hours_remaining: 1.0 to 48.0 hours
    Target:
    - triage_action:
        0: STABLE_MONITOR (Nominal)
        1: DIVERT_AMBULANCES (Capacity overflow)
        2: EXPEDITE_SUPPLY_CHAIN (Resource deficit)
        3: EVACUATE_WARD_IMMEDIATE (Catastrophic collapse)
    """
    random.seed(42)
    np.random.seed(42)
    rows = []

    for _ in range(n_samples):
        # Baseline normal hospital values
        icu_occupancy = random.uniform(50.0, 85.0)
        o2_hours = random.uniform(18.0, 60.0)
        vent_pct = random.uniform(40.0, 75.0)
        trauma_surge = random.uniform(0.05, 0.35)
        blood_units = random.randint(30, 90)
        generator_hours = random.uniform(12.0, 36.0)
        action = 0  # STABLE_MONITOR

        r = random.random()
        if r < 0.10:
            # Scenario: Catastrophic Grid & Life Support Collapse -> EVACUATE
            generator_hours = random.uniform(0.5, 3.5)
            o2_hours = random.uniform(0.5, 3.0)
            icu_occupancy = random.uniform(90.0, 100.0)
            action = 3  # EVACUATE_WARD_IMMEDIATE
        elif r < 0.22:
            # Scenario: Critical Supply Chain Deficit (Blood/Diesel)
            blood_units = random.randint(0, 5)
            generator_hours = random.uniform(2.0, 3.9)
            action = 2  # EXPEDITE_SUPPLY_CHAIN
        elif r < 0.35:
            # Scenario: Ward Overflow / Mass Casualty Surge -> DIVERT
            icu_occupancy = random.uniform(92.0, 100.0)
            vent_pct = random.uniform(90.0, 100.0)
            trauma_surge = random.uniform(0.70, 0.99)
            action = 1  # DIVERT_AMBULANCES

        rows.append({
            "icu_bed_occupancy_pct": round(icu_occupancy, 1),
            "oxygen_hours_remaining": round(o2_hours, 1),
            "ventilator_utilization_pct": round(vent_pct, 1),
            "trauma_surge_index": round(trauma_surge, 2),
            "blood_o_neg_units": blood_units,
            "generator_hours_remaining": round(generator_hours, 1),
            "triage_action": action
        })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} synthetic medical triage samples -> {csv_path}")
    return df

def train_medical_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, '..', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)

    csv_path = os.path.join(artifacts_dir, 'synthetic_medical_triage_5k.csv')
    df = generate_medical_dataset(csv_path, n_samples=5000)

    features = [
        "icu_bed_occupancy_pct",
        "oxygen_hours_remaining",
        "ventilator_utilization_pct",
        "trauma_surge_index",
        "blood_o_neg_units",
        "generator_hours_remaining"
    ]
    X = df[features]
    y = df["triage_action"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n--- Training Clinical Disaster Triage Random Forest Model ---")
    model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    action_labels = ["STABLE_MONITOR", "DIVERT_AMBULANCES", "EXPEDITE_SUPPLY", "EVACUATE_WARD"]
    print("Clinical Triage Evaluation Matrix:")
    print(classification_report(y_test, y_pred, target_names=action_labels, digits=4))

    acc = float(accuracy_score(y_test, y_pred))

    # Export Model Artifact
    model_path = os.path.join(artifacts_dir, 'medical_triage_model.pkl')
    joblib.dump(model, model_path)
    print(f"Exported medical triage model artifact -> {model_path}")

    # Export Metadata
    meta_path = os.path.join(artifacts_dir, 'medical_triage_metadata.json')
    metadata = {
        "model_name": "ProjectSyn-ClinicalDisasterTriage",
        "model_type": "RandomForestClassifier",
        "n_estimators": 100,
        "accuracy": acc,
        "features": features,
        "action_codes": {
            0: "STABLE_MONITOR (Nominal ICU & Ward operations)",
            1: "DIVERT_AMBULANCES (Capacity surge; engage Dijkstra corridor diversion)",
            2: "EXPEDITE_SUPPLY_CHAIN (Critical O-Neg blood or diesel replenishment alert)",
            3: "EVACUATE_WARD_IMMEDIATE (Catastrophic power/oxygen failure; immediate patient airlift)"
        },
        "target": "triage_action"
    }
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Exported clinical triage metadata -> {meta_path}")

    return model, metadata

if __name__ == "__main__":
    train_medical_model()
