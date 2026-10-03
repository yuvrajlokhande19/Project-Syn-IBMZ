# AegisCore Development TODO & Strategy

## Pair 1 (Command Center)
- [x] Integrate Mapbox/CARTO base layers.
- [x] Wire up Cyber Attack Triggers (Payload Tamper, Replay, Stale, Spoofing).
- [x] Add 3-Level Sovereignty Toggles.
- [ ] Add "Resource Allocation" tab indicating which ICU beds have the most active backup power.
- [ ] Render actual `Dijkstra` routes visually on the map (drawing paths between hospitals instead of just markers).

## Pair 2 (Logic & ML Engine)
- [x] Write `data_generator.py` and `synthetic_hospital_data_10k.csv`.
- [x] Implement deterministic Dijkstra Algorithm.
- [x] Train IBM Snap ML / Random Forest `.pkl`.
- [x] Ensure simulator pumps out `nonces` and `timestamps`.
- [ ] Add `Hyper-local Weather Corroboration` to the simulator (inject mock OpenWeatherAPI JSON blocks to merge with the sensor data).
- [ ] Stress Testing: Push `load_tester.py` to blast 1000 events/second.

## Pair 3 (Mainframe Core)
- [x] Build `FastAPI` async ingestion pipeline.
- [x] Tamper-Evident CPACF SQLite Ledger.
- [x] Multilingual Translation (EN, HI, MR).
- [x] P0 Trusted Telemetry Gate (Nonces, HMAC, Timestamps).
- [x] Cross-Sensor Validation / False Positive Filtering.
- [ ] Build `/api/metrics` endpoint exposing Mainframe CPU latency and throughput for the UI.
- [ ] Compile Llama.cpp for actual `s390x` execution (Requires 2 hours+ of local compilation time; defer until after submission freeze).
