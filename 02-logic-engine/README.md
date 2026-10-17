# Project Syn — Pair 2: Data Logic & ML Engine
### Subsystem Documentation | IBM Z Datathon 2026

---

## 1. Executive Summary

**Project Syn** is an air-gapped urban resilience and disaster triage engine engineered to maintain civic healthcare operations during major infrastructure disruptions, including urban flooding, power grid blackouts, and concurrent cyber attacks.

The architecture comprises three integrated subsystems:
- **Pair 1: Command Center (`01-command-center/`)**: Nothing OS-styled operations dashboard with live telemetry feeds and GIS hospital mapping.
- **Pair 2: Data Logic & ML Engine (`02-logic-engine/`)**: Telemetry simulation, edge HMAC-SHA256 signing, machine learning anomaly detection, and deterministic routing.
- **Pair 3: Mainframe Core (`03-mainframe-core/`)**: IBM LinuxONE `s390x` FastAPI ingestion gateway, CPACF-accelerated audit ledger, local multilingual LLM translation, and Telegram alerts.

### Pair 2 Core Responsibilities
1. **Telemetry Simulation**: Emulating real-world ICU and municipal telemetry using harmonic functions and physical anomaly scenarios.
2. **Edge Cryptographic Signing**: Computing HMAC-SHA256 signatures over raw JSON payload bytes to verify source authenticity before mainframe ingestion.
3. **Machine Learning Pipeline**: Generating structured telemetry datasets, training anomaly detection models (Isolation Forest / Random Forest), and exporting reproducible artifacts.
4. **Deterministic Emergency Routing**: Calculating safe ambulance corridors using Dijkstra's algorithm with dynamic flood penalties. To guarantee life safety, routing decisions remain strictly deterministic.

---

## 2. Architecture and Data Flow

```
+-----------------------------------------------------------------------------+
|                       PAIR 2: DATA LOGIC & ML ENGINE                        |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [ generate_dataset.py ] -------> artifacts/synthetic_hospital_data_10k.csv |
|                                                    |                        |
|                                                    v                        |
|                                            [ train_ml.py ]                  |
|                                                    |                        |
|                        +---------------------------+---------------------+  |
|                        |                           |                     |  |
|                        v                           v                     v  |
|               anomaly_model.pkl           random_forest.pkl     model_metadata.json
|               (Isolation Forest)          (Supervised RF)                   |
|                                                                             |
|  [ telemetry_simulator.py ]                                                 |
|        |                                                                    |
|        +---> 1. Generate Telemetry (Voltage, Flood Index, Route Congestion) |
|        +---> 2. Canonical JSON Serialization                                |
|        +---> 3. Compute HMAC-SHA256 over raw JSON payload bytes             |
|        +---> 4. Transmit HTTP POST with 'X-Signature' header                |
|                                                                             |
|  [ routing_algorithm.py ]                                                   |
|        |                                                                    |
|        +---> 5-Node Nagpur Hospital Topology                                |
|        +---> Dynamic Flood Penalty Injection (+999 on flooded edges)        |
|        +---> Deterministic Dijkstra Corridor Calculation                    |
+-----------------------------------------------------------------------------+
                                       |
                     HTTP POST /api/telemetry/ingest
                     Headers: Content-Type: application/json
                              X-Signature: <64-character hex>
                                       v
+-----------------------------------------------------------------------------+
|                       PAIR 3: MAINFRAME CORE (s390x)                        |
|                                                                             |
|  [ main.py ] --------> 1. Verify HMAC-SHA256 against raw body bytes         |
|                        2. Ingest verified payload into asyncio.Queue        |
|                                     |                                       |
|  [ queue_worker.py ] <--------------+                                       |
|        |                                                                    |
|        +---> 3. Append to SQLite Hash Ledger (CPACF audit chain)            |
|        +---> 4. Trigger Alerts via telegram_dispatch.py (Flood > 0.8)       |
+-----------------------------------------------------------------------------+
                                       |
                     HTTP GET /api/telemetry/live
                                       v
+-----------------------------------------------------------------------------+
|                        PAIR 1: COMMAND CENTER (UI)                          |
|                                                                             |
|  [ index.html ] -----> Live Telemetry Stream, Hash Ledger Feed,             |
|                        Interactive Hospital Map, Alert Overlays             |
+-----------------------------------------------------------------------------+
```

---

## 3. Subsystem Implementation Status

| Component | Target Description | File Path | Status | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Telemetry Generator** | Harmonic wave and noise modeling for grid voltage, flood, and congestion | `src/telemetry_simulator.py` | Complete | Verified locally |
| **Edge HMAC Signer** | HMAC-SHA256 computed over raw serialized JSON payload bytes | `src/telemetry_simulator.py` | Complete | Verified locally |
| **Transmission Protocol** | HTTP POST transmission using `X-Signature` authentication header | `src/telemetry_simulator.py` | Complete | Byte-compatible with Pair 3 `main.py` |
| **Dataset Generator** | 10,000-record synthetic telemetry generator with disaster scenarios | `src/generate_dataset.py` | Complete | Verified (10,000 rows, 0 nulls) |
| **ML Training Pipeline** | Anomaly detection training for Isolation Forest and Random Forest | `src/train_ml.py` | Complete | Verified (Exports `.pkl` and metadata) |
| **Model Artifacts** | Serialized ML models and metadata exported to `artifacts/` | `artifacts/` | Complete | Verified reloadable via `joblib` |
| **Deterministic Router** | Dijkstra shortest path with dynamic flood penalty injection | `src/routing_algorithm.py` | Complete | Verified (Corridor rerouting verified) |
| **Pipeline Test Suite** | 7-stage automated validation covering data, models, and metadata | `tests/test_pipeline.py` | Complete | Verified (7/7 tests passing) |
| **Runtime Launcher** | Automated Windows batch launcher for the telemetry simulator | `start_simulator.bat` | Complete | Verified syntax |
| **Mainframe Gateway** | Live ingestion via `http://148.100.112.151:8000/api/telemetry/ingest` | `src/telemetry_simulator.py` | Configured | Gateway availability dependent |

---

## 4. Repository Structure

```
02-logic-engine/
│
├── artifacts/                                # Serialized models, datasets, and metadata
│   ├── anomaly_model.pkl                     # Deployed Isolation Forest model artifact
│   ├── isolation_forest.pkl                  # Preserved Isolation Forest model artifact
│   ├── random_forest.pkl                     # Supervised Random Forest benchmark model
│   ├── model_metadata.json                   # Model specifications, feature order, and metrics
│   └── synthetic_hospital_data_10k.csv       # 10,000-record synthetic telemetry dataset
│
├── src/                                      # Core algorithmic source code
│   ├── generate_dataset.py                   # Synthetic telemetry dataset generator
│   ├── routing_algorithm.py                  # Hospital network topology and Dijkstra router
│   ├── telemetry_simulator.py                # Telemetry generator, HMAC signer, and HTTP streamer
│   └── train_ml.py                           # Model training and artifact serialization script
│
├── tests/                                    # Automated verification suite
│   └── test_pipeline.py                      # Pipeline test suite (data integrity, inference, metadata)
│
├── README.md                                 # Subsystem documentation and integration reference
├── requirements.txt                          # Python dependencies for Pair 2
└── start_simulator.bat                       # Launcher script for telemetry streaming
```

---

## 5. Environment and Dependencies

### Prerequisites
- **Python**: Version 3.10 or higher.
- **Operating System**: Platform-independent (tested on Windows x86_64; compatible with Linux and IBM LinuxONE `s390x`).

### Installation
From the `02-logic-engine` directory, install required packages:

```bash
pip install -r requirements.txt
```

### Dependency Manifest (`requirements.txt`)
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `scikit-learn>=1.3.0`
- `joblib>=1.3.0`
- `httpx>=0.24.0`

---

## 6. Execution Guide

All commands are executed from the `02-logic-engine/` directory.

### Generate Synthetic Dataset
```bash
python src/generate_dataset.py
```
Generates `artifacts/synthetic_hospital_data_10k.csv` (10,000 rows of structured telemetry).

### Train and Export Models
```bash
python src/train_ml.py
```
Trains the models, displays classification metrics, and exports artifacts to `artifacts/`.

### Run Pipeline Verification Tests
```bash
python tests/test_pipeline.py
```
Executes the 7 automated verification tests across data schema, inference boundaries, and metadata compliance.

### Run Deterministic Routing Demonstration
```bash
python src/routing_algorithm.py
```
Calculates normal routing between AIIMS and Mayo Hospital, applies a flood penalty to GMC Nagpur, and displays the recalculated corridor.

### Launch Telemetry Streamer
```bash
# Using the Windows batch script:
start_simulator.bat

# Or directly with Python:
python -u src/telemetry_simulator.py
```
Streams HMAC-signed telemetry packets to the configured ingestion endpoint at two-second intervals.

---

## 7. Telemetry and Cryptographic Specification

### Payload Schema
Telemetry packets generated by `src/telemetry_simulator.py` adhere to the canonical schema:

```json
{
  "packet_id": "SYN-4821",
  "timestamp": "2026-10-17T17:04:11.123456+00:00",
  "sensor_location": "GMC_Nagpur",
  "metrics": {
    "grid_voltage": 218.45,
    "flood_index": 0.12,
    "route_congestion": 45
  },
  "status": "nominal"
}
```

### Field Definitions
- `packet_id` *(string)*: Unique identifier prefixed with `SYN-` followed by an integer.
- `timestamp` *(string)*: ISO-8601 UTC timestamp generated at time of emission.
- `sensor_location` *(string)*: Monitored hospital node (`GMC_Nagpur`, `Mayo_Hospital`, `AIIMS_Nagpur`, `Lata_Mangeshkar_Hospital`, `Wockhardt_Hospital`).
- `metrics.grid_voltage` *(float)*: Power supply voltage in Volts (nominal: ~216–224V; blackout: 20–85V).
- `metrics.flood_index` *(float)*: Normalized flood indicator from 0.0 to 1.0 (nominal: <0.25; emergency threshold: >0.80).
- `metrics.route_congestion` *(integer)*: Correlated road corridor congestion percentage (10% to 95%).
- `status` *(string)*: Node status flag (`"nominal"` if `flood_index <= 0.8`, `"critical"` if `> 0.8`).

### Verified HMAC-SHA256 Authentication Contract
To prevent tampering or data injection at the network perimeter, telemetry is signed prior to transmission:
1. **Serialization**: `payload_bytes = json.dumps(packet).encode('utf-8')` converts the dictionary into raw UTF-8 JSON bytes.
2. **Signature Calculation**: HMAC-SHA256 is computed over `payload_bytes` using `SECRET_KEY = b"mainframe_secret_key"`.
3. **Transmission**: Sent via HTTP POST with `content=payload_bytes` and header `X-Signature: <64-character hex>`.
4. **Receiver Compatibility**: In `03-mainframe-core/main.py`, the endpoint extracts raw bytes via `body = await request.body()`, recomputes the HMAC-SHA256 with the same secret key, and compares it against `request.headers.get("X-Signature")` via `hmac.compare_digest`. Because `content=payload_bytes` transmits the exact serialized bytes, the sender and receiver bytes match identically.

---

## 8. Machine Learning Pipeline and Artifacts

### Dataset Overview (`synthetic_hospital_data_10k.csv`)
- **Sample Count**: 10,000 records (0 null, missing, or non-finite values).
- **Class Balance**: 9,595 nominal records (~96.0%) and 405 anomaly records (~4.0%).
- **Scenarios**: Baseline hospital telemetry, flash flood emergencies (`flood_index > 0.8`), and grid blackouts (`grid_voltage` 20–85V).

### Model Training Configuration
- **Primary Model**: `IsolationForest` (`n_estimators=100`, `contamination=0.0405`, `random_state=42`).
- **Benchmark Model**: `RandomForestClassifier` (`n_estimators=100`, `random_state=42`).
- **Feature Vector**: Strict 3-feature ordering:
  ```python
  features = ['grid_voltage', 'flood_index', 'route_congestion']
  ```
- **Exported Artifacts**:
  - `artifacts/anomaly_model.pkl`: Primary deployed model artifact.
  - `artifacts/isolation_forest.pkl`: Dedicated Isolation Forest artifact.
  - `artifacts/random_forest.pkl`: Supervised Random Forest benchmark.
  - `artifacts/model_metadata.json`: Feature ordering and training metadata.

*Evaluation Note*: Model metrics were evaluated on synthetic telemetry representing modeled operational and disaster conditions.

---

## 9. Deterministic Routing Engine

To ensure predictable and fail-safe ambulance corridor calculation, navigation logic uses Dijkstra's shortest-path algorithm across five medical centers in Nagpur: `GMC_Nagpur`, `Mayo_Hospital`, `AIIMS_Nagpur`, `Lata_Mangeshkar_Hospital`, and `Wockhardt_Hospital`.

### Dynamic Flood Rerouting
When a node reports severe flooding (`flood_index > 0.8`), `update_weights(flooded_location, penalty=999)` applies an environmental cost penalty to all connecting corridors:
- **Normal Corridor (AIIMS to Mayo)**: `AIIMS_Nagpur -> GMC_Nagpur -> Mayo_Hospital` (Cost: `17`)
- **Flooded Condition at GMC Nagpur (Penalty +999)**: `AIIMS_Nagpur -> Lata_Mangeshkar_Hospital -> Wockhardt_Hospital -> Mayo_Hospital` (Cost: `22`)

---

## 10. Integration Specifications & ML Integration Notes

### Integration with Pair 1 (Command Center)
- **GIS Alignment**: Hospital node coordinates in `routing_algorithm.py` match the Leaflet map markers in `01-command-center/index.html`.
- **Data Ingestion**: The frontend dashboard polls Pair 3's `/api/telemetry/live` endpoint to display verified telemetry and hash ledger blocks.

### Integration with Pair 3 (Mainframe Core)
- **Ingestion Endpoint**: `POST /api/telemetry/ingest`
- **Authentication**: Pair 3 validates the `X-Signature` header against the raw body bytes before queuing the payload for audit ledger logging and alert dispatch.

### ML Integration & Queue Worker Status
- **Current Mainframe Behavior**: In `03-mainframe-core/queue_worker.py`, incoming telemetry from the queue is recorded into SQLite via `HashLedger.record_telemetry(data)` and forwarded to `telegram_dispatch.process_and_alert(data)`. Alerting currently relies on an emergency threshold heuristic (`flood_index > 0.8`). Live ML inference has not yet been integrated into `queue_worker.py`.
- **Model Output Conventions for Future Integration**:
  - `IsolationForest` outputs `+1` for nominal inliers and `-1` for anomalies. When Pair 3 connects model inference, anomalies must be evaluated via `prediction[0] == -1` (or mapped to binary `1`).
  - `RandomForestClassifier` outputs standard binary labels (`0` = nominal, `1` = anomaly).
- **Deployment**: Telemetry and routing run on standard Python 3.10+ environments. On IBM LinuxONE `s390x`, models can leverage IBM Snap ML for hardware acceleration, and the ledger benefits from native CPACF cryptographic coprocessor instructions.

---

## 11. Verification and Test Results

The pipeline test suite in `tests/test_pipeline.py` executes 7 automated validation phases:

```bash
python tests/test_pipeline.py
```

| Phase | Test Description | Condition Checked | Result |
| :--- | :--- | :--- | :--- |
| **Test 1** | Dataset Existence & Size | `len(df) == 10000` | Passed |
| **Test 2** | Column Schema | 7 canonical telemetry columns | Passed |
| **Test 3** | Data Integrity | Zero null or infinite values | Passed |
| **Test 4** | Anomaly Distribution | 9,595 nominal (0), 405 anomaly (1) | Passed |
| **Test 5** | Artifact Loading | `joblib.load('artifacts/anomaly_model.pkl')` | Passed |
| **Test 6** | Boundary Inference | Nominal $= +1$, Flood Anomaly $= -1$, Blackout Anomaly $= -1$ | Passed |
| **Test 7** | Metadata Alignment | Feature vector: `['grid_voltage', 'flood_index', 'route_congestion']` | Passed |

*Status: All 7 verification tests passed successfully.*

---

## 12. Subsystem Ownership and Scope

- **Pair 2 Ownership**: Pair 2 maintains all scripts and artifacts within `02-logic-engine/` (`src/`, `artifacts/`, `tests/`, `requirements.txt`, and `start_simulator.bat`).
- **Team Boundaries**: Pair 2 does not modify frontend files in `01-command-center/` or backend server implementations in `03-mainframe-core/`. Shared interfaces (`SECRET_KEY`, feature vector ordering, and the `X-Signature` header contract) are maintained collaboratively across pairs.
