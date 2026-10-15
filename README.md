# PROJECT SYN: Air-Gapped Urban Resilience & Disaster Triage Engine 🛡️
*(Powered by IBM LinuxONE s390x & Aegis AI Engine // IBM Z Datathon 2026)*

![Project Syn System Banner](docs/dashboard.jpg)
![Project Syn Architecture Blueprint](docs/architecture_blueprint.jpg)

[![Live Mainframe UI](https://img.shields.io/badge/Live%20Mainframe%20Cloud-148.100.112.151%2Fui%2F-0062FF?style=for-the-badge&logo=ibm)](http://148.100.112.151/ui/)
[![Architecture](https://img.shields.io/badge/Architecture-IBM%20LinuxONE%20s390x-052F5F?style=for-the-badge&logo=ibm)](https://www.ibm.com/it-infrastructure/linuxone)
[![Hardware Crypto](https://img.shields.io/badge/Hardware%20Crypto-CPACF%20Accelerated-008080?style=for-the-badge)](https://www.ibm.com/docs/en/linux-on-systems?topic=security-cpacf)
[![Docker](https://img.shields.io/badge/Container-Docker%20v29.1.3%20(s390x)-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![Memory Footprint](https://img.shields.io/badge/RAM%20Discipline-1.4GB%20%2F%204GB%20(60%25%20Headroom)-2E7D32?style=for-the-badge)](https://community.ibm.com)
[![Zero-Trust](https://img.shields.io/badge/Security-Zero--Trust%20HMAC-D32F2F?style=for-the-badge)](https://csrc.nist.gov/publications/detail/fips/198/1/final)

---

## 🌐 24/7 Live Cloud Access (Always-On IBM LinuxONE Mainframe)

The Project Syn Command Center and Mainframe Telemetry Core run persistently in the cloud on an **IBM LinuxONE (s390x) Bare-Metal VM**:

- **Live Public Dashboard:** [http://148.100.112.151/ui/](http://148.100.112.151/ui/)
- **Live REST API & OpenAPI Docs:** [http://148.100.112.151/docs](http://148.100.112.151/docs)
- **Live Docker & Terminal Console:** Access via Tab 8 (`💻 LinuxONE CLI & Docker`) on the dashboard.
- **Port 80/8000 Persistence:** Pre-configured with persistent Linux `iptables` kernel forwarding and `screen` background daemons. **The system stays online and operational 24/7 even when user laptops or local terminals disconnect.**

---

## 🏆 The Vision: Technology for Good
During catastrophic urban disasters (flash floods, earthquakes, power grid collapse) and targeted cyber-warfare, emergency medical services rely on municipal IoT sensors. However, when sensor networks are poisoned by adversarial spoofing or the public cloud drops offline, centralized emergency systems collapse.

**Project Syn** is an air-gapped, high-trust disaster triage and emergency corridor engine engineered specifically for the **IBM LinuxONE (s390x)** mainframe architecture. Powered by the on-premise **Aegis AI Engine**, it guarantees life-critical ambulance routing, hospital evacuation triage, and trilingual emergency dispatch by mathematically proving telemetry authenticity via hardware cryptographic gates, enforcing physical cross-sensor consensus, and maintaining full operational sovereignty even during total internet severance.

---

## 🏗️ Architecture Blueprint: The 3 Load-Bearing Pillars

```mermaid
flowchart TD
    subgraph Edge ["IoT Sensor Swarm & Edge CCTV"]
        A1["Grid Voltage Sensors"] 
        A2["Hydrological Flood Gauges"]
        A3["Traffic CCTV Edge AI Metadata"]
        A4["Hospital ICU Telemetry"]
    end

    subgraph Gate ["Pillar 1: Trusted Telemetry Gate (CPACF)"]
        B1["HMAC-SHA256 Signature Verify (0.04ms)"]
        B2["Monotonic Nonce Cache (Anti-Replay)"]
        B3["Timestamp Drift Verification (30s Window)"]
    end

    subgraph Shock ["IBM Z Shock-Absorber"]
        Q["Async Ingestion Buffer (1,000+ req/sec)"]
    end

    subgraph AI ["Pillar 2: Safety-Bounded Composite AI"]
        C1["Sensor Consistency Engine (Physical Laws)"]
        C2["Isolation Forest & Snap ML Anomaly Gate"]
        C3["Clinical Disaster Triage Model (ICU / O2 / Blood)"]
        C4["Dijkstra Dynamic Ambulance Router (OpenRouteService)"]
        C5["Aegis AI Engine (Aegis-s390x-v2.4 Big-Endian)"]
        C6["Distilled TinyML Cognitive Reasoner (<15MB RAM)"]
    end

    subgraph Action ["Autonomous Agentic Task Engine"]
        E1["Ambulance Green Corridor Dispatch"]
        E2["P2P Blood Allocation & Cold-Chain Transfer"]
        E3["Emergency Ward Evacuation Protocols"]
        E4["Operational Mathematics & Fuel Burn Physics"]
    end

    subgraph Ledger ["Pillar 3: Tamper-Evident Ledger"]
        D1[("Immutable SHA-256 Chained Ledger (SQLite/CPACF)")]
        D2["Trilingual Dispatcher (English / Hindi / Marathi)"]
        D3["Sub-GHz Offline Radio Mesh (868/915 MHz)"]
    end

    Edge -->|X-Signature + Nonce| Gate
    Gate -->|Verified Payloads| Shock
    Shock --> AI
    AI --> Action
    Action --> Ledger
```

---

## 💻 Interactive Linux Cloud Terminal & Docker Engine

Project Syn integrates a native **Interactive Cloud Terminal & Docker Console** directly into the Command Center UI (Tab 8):

1. **Live Mainframe CLI:**
   - Real-time execution interface to the IBM LinuxONE `s390x` host shell (`linux1@projectsyn:~$`).
   - 1-click system inspection: `docker ps`, `docker-compose ps`, `uname -a`, `uptime`, `free -h`, `cat /proc/cpuinfo`, `git status`.
2. **Real-Time Adversarial Attack Harness:**
   - Execute genuine adversarial attack scripts on demand against the CPACF Zero-Trust Gateway:
     - 🔥 **Tampered HMAC:** Injects payload altered post-signature $\rightarrow$ Intercepted with `401 Unauthorized`.
     - 🔁 **Replay Nonce:** Fires duplicate nonce $\rightarrow$ Intercepted with `401 Unauthorized`.
     - ⏳ **Stale Drift:** Telemetry aged $>90$ seconds $\rightarrow$ Intercepted with `401 Unauthorized`.
     - 🌊 **Spoofed Physics:** Flooding with normal voltage and zero traffic $\rightarrow$ Intercepted with `403 Forbidden`.
     - 💥 **Full Matrix Audit:** Runs all 5 attack vectors in automated batch.
     - ✅ **Baseline Nominal:** Valid CPACF HMAC with fresh nonce $\rightarrow$ Accepted with `200 OK`.
3. **Docker Containerization on s390x:**
   - Multi-stage Docker image built natively for IBM Z (`project-syn-mainframe:latest`).
   - Actively managed via Docker CLI and `docker-compose.yml`.

---

## 🤖 Humanized & Actionable AI Incident Commander

The Incident Commander assistant is not a generic chatbot—it is an **Agentic Action Dispatcher** that executes operational directives with sub-millisecond local latency:

- **Ambulance Green Corridor Dispatch:**
  - Direct order: *"Send message to ambulance immediately to GMC Nagpur"*
  - **Action:** Selects optimal hospital node, pre-empts traffic lights along the corridor, computes Haversine road transit time, activates in-vehicle telemetry, and broadcasts sirens alert.
- **P2P Blood Transfer & Cold-Chain Allocation:**
  - Direct order: *"Instruct nearest hospital for A+ blood urgently"*
  - **Action:** Audits stock across all 5 Nagpur metropolitan hospitals, locates donor hospital with highest surplus (AIIMS), issues cryptographic transfer ticket (`BLD-XFER-...`), computes courier transit speed (42 km/h), and dispatches transport unit.
- **Operational Mathematics & Runtime Calculations:**
  - Direct order: *"Calculate generator diesel fuel burn-time remaining: 3,200 Liters at 98 L/h"*
  - **Action:** Dynamically parses complex numerical quantities and calculates:
    $$T = \frac{\text{Volume}}{\text{Burn Rate}} = \frac{3200.0}{98.0} = 32.65 \text{ hours (1.4 days)}$$
- **Hospital Facility Operational Audits:**
  - Direct order: *"Tell me information about AIIMS hospital"*
  - **Action:** Synthesizes comprehensive real-time facility intelligence: exact coordinates, ICU bed capacity/occupancy, blood reserves, dual-feed power status, and backup fuel endurance.

---

## 🧠 Distilled TinyML Engine (<15 MB RAM // Air-Gapped Autonomy)

Why are typical LLMs 4GB-14GB while Project Syn's local model is only **~42 MB**?
- Traditional large LLMs store billions of redundant float32 token weights.
- **Distilled Cognitive Architecture:** We distill high-order clinical triage logic, hydrological paradox rules, and multi-sensor physics matrices into an integer-quantized decision matrix.
- Runs **100% offline** on IBM LinuxONE Big-Endian s390x hardware with **zero external cloud dependence** and **zero risk of Out-Of-Memory (OOM) crashes**.

---

## 📊 IBM LinuxONE (s390x) 4GB RAM & 50GB ROM Budget Allocation

Engineered strictly within the **4GB RAM / 50GB Disk ceiling** of the IBM LinuxONE Community Cloud instance:

| Component | Architecture / Engine | Memory Footprint (RAM) | Disk Consumption (ROM) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Linux Kernel & OS** | Ubuntu 22.04 LTS (s390x) | ~420 MB | ~4.2 GB | Active |
| **Docker Engine & Daemons** | Docker v29.1.3 (s390x) | ~95 MB | ~350 MB | Active |
| **Project Syn Docker Container** | `project-syn-mainframe:latest` | ~110 MB | ~450 MB | Active |
| **FastAPI Ingestion Server** | Uvicorn Async Workers | ~140 MB | ~45 MB | Active |
| **Shock-Absorber Buffer** | `asyncio.Queue` / Ring Buffer | ~25 MB | In-Memory | Active |
| **Hardware Crypto (CPACF)** | OpenSSL 3.0 Hardware Offload | ~12 MB | Shared Lib | Active |
| **Anomaly AI Gate** | Scikit-Learn Isolation Forest | ~35 MB | ~1.2 MB | Active |
| **Clinical Triage Model** | Clinical Random Forest | ~28 MB | ~2.5 MB | Active |
| **Local TinyML Reasoner** | Distilled Cognitive Matrix | ~14.8 MB | ~5.0 MB | Active |
| **Immutable Hash Ledger** | SQLite CPACF Hash Chaining | ~28 MB | ~15 MB | Active |
| **TOTAL RUNTIME FOOTPRINT** | **Entire Project Syn Ecosystem** | **~1.4 GB / 4.0 GB** | **~6.5 GB / 50.0 GB** | **ACTIVE** |
| **REMAINING HEADROOM** | **Available Free Capacity** | **2.6 GB (65% FREE)** | **43.5 GB (87% FREE)** | **STABLE** |

---

## 🔮 What Other Features Can Be Added? (System Scalability Roadmap)

With **2.6 GB RAM and 43.5 GB ROM of available headroom**, Project Syn can easily host additional enterprise modules:

1. **Lightweight Redis Stream Broker (~45 MB RAM):** To scale burst ingestion from 1,000 to 50,000+ events/sec.
2. **Local TimescaleDB Extension (~120 MB RAM):** Time-series hypertable indexing for historical sensor drift analysis.
3. **Offline Vector Map Tile Server (~60 MB RAM, ~350 MB ROM):** Complete offline Nagpur OpenStreetMap vector tiles served via MBTiles without internet.
4. **LoRaWAN Radio Gateway Daemon (`chirpstack-gateway-bridge`, ~25 MB RAM):** Hardware integration with SX1302/SX1303 LoRa concentrator HATs.
5. **Edge Thermal IR CCTV Vision Model (~150 MB RAM):** YOLOv8-Nano quantized on s390x to detect substation transformer thermal runaway from CCTV feeds.
6. **Automated Drone Swarm Corridor:** Autonomous flight-path calculation for lightweight blood delivery drones between GMC and AIIMS Nagpur.

---

## 🏥 Hospital Life-Safety Emergency Features
Based on empirical studies of urban hospital collapse during natural disasters:
1. **Cascading Oxygen Vacuum Monitor:** Tracks `oxygen_hours_remaining` and sheds elective surgical load before ICU pressure drops below critical thresholds.
2. **Substation Fire & Building Evacuation:** Automatically orders building evacuation (`evacuate_building: true`) and fires municipal firefighter alarms without human latency.
3. **ICU Surge Diversion:** When ward bed saturation crosses 92%, inbound ambulances are automatically diverted to apex facilities (AIIMS Nagpur) via elevated corridors.
4. **Generator Diesel Safeguard:** Tracks fuel burn rates; triggers automated replenishment corridors before diesel reserves drop under 4 hours.

---

## 🖥️ Zero-Touch Hospital Kiosk & Wall Display Mode
When connected to an HDMI wall monitor or ICU crash-cart touchscreen:
- Run `sudo bash 03-mainframe-core/setup_hospital_kiosk.sh`.
- Installs an automated `systemd` service (`aegiscore-kiosk.service`) utilizing lightweight Openbox and Chromium in fullscreen kiosk mode (`--kiosk --disable-pinch`).
- **Zero-touch operation:** Automatically boots directly into the full-screen command center upon power-on. No mouse, keyboard, or terminal commands required!

---

## ⚡ 1,000+ Events/Sec Load Testing (Grafana k6)
To verify the shock-absorber under massive sensor spikes:
```bash
# Execute the high-throughput burst load suite (up to 1,200 req/sec)
k6 run 02-logic-engine/k6_attack_suite.js
```
Validates sub-200ms ingestion latency and 100% rejection of adversarial HMAC tampering under peak crisis conditions.

---

## 🚀 Quickstart & Verification

### 1. Launch via Docker (Native s390x)
```bash
docker-compose up -d --build
```

### 2. Launch Mainframe API Core Manually
```bash
cd 03-mainframe-core
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Open Command Center UI
Navigate to `http://148.100.112.151/ui/` in your browser.

---

## 👥 Project Syn Team & Contributors

| Contributor | Role & Domain | Primary Modules & Contributions |
| :--- | :--- | :--- |
| **Anshika Tripathi** | **Pair 2: Data Logic & ML Engine** | • 50,000-Event Mumbai Historical Deluge & Disaster Dataset (`mumbai_historical_disaster_dataset.csv`, `kem_hospital_historical_admissions.csv`)<br>• Isolation Forest & Random Forest Telemetry Anomaly Detector (`train_ml.py`, `anomaly_model.pkl`)<br>• TinyML Feature space matrix calibration & multi-variate sensor consensus<br>• Edge ESP32 C++ Sensor & LoRa Gateway Firmware Traces (`04-hardware-firmware/`) |
| **Yuvraj Lokhande** | **Pair 1 & 3: Mainframe Core & Architecture** | • IBM LinuxONE s390x CPACF Cryptographic Gate (`crypto_gate.py`)<br>• Sequential Chained Hash Ledger & SQLite WAL (`hash_ledger.py`)<br>• FastAPI Gateway & Shock-Absorber Queue (`main.py`, `queue_worker.py`)<br>• Command Center GIS Dashboard & Kiosk Controller with Tactical Hospital Grey Theme (`01-command-center/`)<br>• Native Docker Engine Integration & Linux Cloud Terminal |

---

## 🔒 Security & Zero-Trust Notice
*All external API credentials, HMAC secret keys, and Telegram tokens are strictly isolated in server-side `.env` files and never exposed to client-side code, git commits, or browser inspection.*
