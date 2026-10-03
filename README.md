

---
### 🌐 LIVE REFERENCE DEMO
**Dashboard Preview:** [https://yuvrajlokhande19.github.io/Project-Syn-IBMZ/01-command-center/index.html](https://yuvrajlokhande19.github.io/Project-Syn-IBMZ/01-command-center/index.html)
*(Use this as the visual baseline for Pair 1 frontend tasks)*
---

# 🛡️ Project Syn: Trustworthy AI for Critical Infrastructure
### *IBM Z Datathon 2026 | Track: Real-Time AI for Critical Decisions (Tech for Good)*

![IBM Z](https://img.shields.io/badge/Architecture-IBM%20s390x%20LinuxONE-052FAD?style=for-the-badge&logo=ibm)
![Security](https://img.shields.io/badge/Security-CPACF%20HMAC--SHA256%20Ledger-green?style=for-the-badge)
![AI Gatekeeper](https://img.shields.io/badge/Cognitive%20Core-IBM%20Snap%20ML-blue?style=for-the-badge)
![LLM Sovereignty](https://img.shields.io/badge/LLM-Big--Endian%20Phi--3-orange?style=for-the-badge)
![Backend](https://img.shields.io/badge/Ingestion-FastAPI%20%2B%20asyncio.Queue-009688?style=for-the-badge&logo=fastapi)
![Frontend](https://img.shields.io/badge/Command%20Center-React%20%2B%20TailwindCSS-61DAFB?style=for-the-badge&logo=react)
![License](https://img.shields.io/badge/Open%20Source-Apache%202.0-yellow?style=for-the-badge)

---

## 🏛️ Executive Summary & Mission

During catastrophic urban disasters (e.g., severe flooding, regional power grid collapses), under-resourced public hospitals suffer cascading failures: unauthenticated sensor tampering misdirects emergency routing, and cloud-bound generative AI models hallucinate life-safety decisions before failing entirely during telecommunications blackouts.

**Project Syn** (*named after the Norse goddess of defensive refusal who bars unauthorized entry*) is an enterprise-grade, safety-bounded disaster resilience engine built natively for the **IBM LinuxONE (`s390x`)** mainframe. 

Rather than blindly trusting AI to make life-critical calls, **Project Syn mathematically bounds the AI**:
1. **Authenticates** incoming telemetry at the edge using cryptographic HMAC signatures before any AI layer sees it.
2. **Detects** infrastructure anomalies at sub-millisecond latency using hardware-accelerated **IBM Snap ML**.
3. **Decides** emergency routes and power triage via **deterministic graph algorithms** (Dijkstra/hard rules).
4. **Translates & Explains** actions into human-readable briefs (English, Hindi, Marathi) via a local, air-gapped **Big-Endian LLM**.
5. **Locks** every transaction into a **Tamper-Evident Audit Chain** accelerated by native **IBM Z CPACF** hardware encryption.

---

## 📐 System Architecture Diagram

```
                                  [ Edge Sensors: CCTV / IoT / Satellite ]
                                                     │
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: SYN FIREWALL (Edge Authentication)                                                            │
│ • Validates payload HMAC-SHA256 signature using edge secrets.                                          │
│ • Spoofed or manipulated payloads (Cyber Attack) ➔ REJECTED IMMEDIATELY.                               │
└──────────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                   │ (Authenticated Telemetry Only)
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: SAFETY-BOUNDED COMPOSITE AI & TRIAGE ENGINE                                                   │
│ ┌───────────────────────────────────────┐   ┌────────────────────────────────────────────────────────┐ │
│ │ 2A. GATEKEEPER: IBM Snap ML           │   │ 2B. DECIDER: Deterministic Graph Engine                │ │
│ │ • Random Forest on s390x (PMML/Conda) │──▶│ • Hard-coded routing & ICU power shedding algorithm    │ │
│ │ • Predicts ward resource depletion    │   │ • Mathematically bounded (Zero Hallucination)          │ │
│ └───────────────────────────────────────┘   └───────────────────────────┬────────────────────────────┘ │
│                                                                         │                              │
│                                                                         ▼                              │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 2C. EXPLAINER: 3 Modes of Sovereignty (Multi-lingual Dispatch)                                     │ │
│ │  [Mode 1: Connected] ➔ OpenRouter Cloud LLM + Telegram Webhook                                     │ │
│ │  [Mode 2: Sovereign] ➔ Local Big-Endian Phi-3 on LinuxONE s390x (No Internet Required)             │ │
│ │  [Mode 3: Degraded]  ➔ Deterministic Rule-Based Emergency Templates (Fallback)                     │ │
│ └────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: TAMPER-EVIDENT AUDIT CHAIN & PERSISTENCE                                                      │
│ • FastAPI `asyncio.Queue` shock absorber prevents SQLite database concurrency write locks.             │
│ • Chained cryptographic record: entry_i = HMAC(secret, prev_hash + payload + decision + timestamp)    │
│ • Powered by native IBM Z CPACF (Central Processor Assist for Cryptographic Functions).               │
└──────────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: 01-COMMAND-CENTER (Military Grade UI)                                                         │
│ • Real-time geospatial hospital command map (Nagpur Regional Hospital).                                │
│ • Live scrolling CPACF cryptographic audit ledger.                                                     │
│ • Interactive "Simulate Cyber Attack" button proving instant threat rejection.                         │
│ • ESG & Green Computing metrics: 94.1% LLM calls avoided via Snap ML gatekeeper.                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📜 The Canonical JSON Data Contract

> **CRITICAL LAW**: All three teams are bound to this exact payload contract. **NO FIELD NAMES OR TYPES MAY BE ALTERED.**

### Inbound Telemetry Payload (`Sensor ➔ Backend`)
```json
{
  "packet_id": "SYN-9942",
  "timestamp": "2026-10-03T18:58:28Z",
  "sensor_location": "Nagpur_Central_ICU",
  "metrics": {
    "grid_voltage": 218.5,
    "flood_index": 0.12,
    "route_congestion": 45
  },
  "nonce": "8f4e2a",
  "hmac_signature": "a8b3f9d2c1..."
}
```

### Outbound Ingestion Response (`Backend ➔ Frontend / Webhook`)
```json
{
  "status": "AUTHENTICATED",
  "packet_id": "SYN-9942",
  "anomaly_detected": true,
  "action_code": "REROUTE_AMBULANCE_CORRIDOR_NORTH",
  "dispatch_brief": {
    "en": "Corridor South flooded. Rerouting Ambulance 04 via North Ring Road to ICU Ward B.",
    "hi": "दक्षिणी गलियारा जलमग्न। एम्बुलेंस 04 को उत्तरी रिंग रोड से आईसीयू वार्ड बी भेजा जा रहा है।",
    "mr": "दक्षिण मार्ग पाण्याखाली. रुग्णवाहिका ०४ उत्तर रिंग रोडने आयसीयू वॉर्ड बी कडे वळवली आहे."
  },
  "sovereignty_mode": "SOVEREIGN_S390X",
  "audit_chain": {
    "block_height": 1241,
    "previous_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "entry_hash": "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35",
    "cpacf_verified": true
  }
}
```

---

## 🚫 RULES OF ENGAGEMENT: STRICT DOMAIN ISOLATION

To eliminate merge conflicts, runtime crashes, and cross-team dependencies during our build sprints:

1. **Zero Cross-Folder Imports**:
   - `01-command-center` **NEVER** imports Python files or accesses SQLite directly.
   - `02-logic-engine` **NEVER** imports FastAPI, starts servers, or renders HTML/JSX.
   - `03-mainframe-core` **NEVER** alters algorithm logic directly; it ingests serialized model binaries (`.pmml` / `.pkl`) produced by Pair 2.
2. **Communication Boundaries**:
   - **Pair 1 ⟷ Pair 3**: Connected strictly via HTTP REST endpoints (`POST /api/telemetry/ingest`, `GET /api/ledger/stream`, `POST /api/simulate-attack`).
   - **Pair 2 ⟷ Pair 3**: Connected strictly via exported artifacts placed in `02-logic-engine/artifacts/` (e.g., `model.pmml`, `routing_rules.json`).
3. **Branch & PR Isolation**:
   - Pair 1 works solely on branch `pair1/frontend`.
   - Pair 2 works solely on branch `pair2/logic-engine`.
   - Pair 3 works solely on branch `pair3/mainframe-core`.
   - Merges into `main` require validation by the Integration Lead (Person 6).

---

## 📂 Repository Topology & Team Responsibilities

```
Project-Syn-IBMZ/
│
├── 01-command-center/            [PAIR 1 ONLY]
│   ├── src/
│   │   ├── components/
│   │   │   ├── CommandMap.jsx           # Geospatial Nagpur Hospital Grid
│   │   │   ├── AuditLedger.jsx          # Live scrolling CPACF SHA-256 Ledger
│   │   │   ├── RedAttackButton.jsx      # Attack Simulation Trigger
│   │   │   └── EsgMetricCards.jsx       # 94.1% Green Computing & Liability Avoided
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── tailwind.config.js
│   ├── package.json
│   └── README.md
│
├── 02-logic-engine/              [PAIR 2 ONLY]
│   ├── data_generator.py                # Telemetry generator with HMAC edge signing
│   ├── attack_injector.py               # Generates spoofed signature & corrupted payloads
│   ├── train_snap_ml.py                 # Trains Random Forest & exports PMML/PKL
│   ├── routing_algorithm.py             # Deterministic Dijkstra / triage graph rules
│   ├── artifacts/                       # Exported model files (model.pmml, rules.json)
│   ├── requirements.txt
│   └── README.md
│
└── 03-mainframe-core/            [PAIR 3 ONLY]
    ├── main.py                          # FastAPI server & route handlers
    ├── queue_worker.py                  # asyncio.Queue shock-absorber for SQLite
    ├── hash_ledger.py                   # CPACF hardware-accelerated SHA-256/HMAC chain
    ├── llm_explainer.py                 # 3 Sovereignty Modes (Cloud / Big-Endian Phi-3 / Templates)
    ├── telegram_dispatch.py             # Webhook dispatcher for EN / HI / MR
    ├── s390x_Miniconda_Setup.md         # Open-source s390x developer deployment guide
    ├── requirements.txt
    └── README.md
```

---

## 🤖 AGENT DIRECTIVES: COPY-PASTE PROMPTS FOR EACH PAIR

Copy and paste the exact prompt block below into your respective pair's AI coding assistant (Google Antigravity, OpenCode, Claude, ChatGPT, etc.) before writing a single line of code.

### 📋 Prompt for PAIR 1: Frontend Command Center
```markdown
You are the dedicated Senior Frontend Engineer for Pair 1 on Project Syn (IBM Z Datathon 2026).
YOUR TERRITORY: `01-command-center/` ONLY.

STRICT ISOLATION CONSTRAINTS:
1. You MUST NOT write any Python code, backend APIs, or direct SQLite connections.
2. You consume data EXCLUSIVELY via HTTP REST requests or mock JSON adhering to the Canonical Data Contract:
   {
     "packet_id": "SYN-9942",
     "timestamp": "2026-10-03T18:58:28Z",
     "sensor_location": "Nagpur_Central_ICU",
     "metrics": { "grid_voltage": 218.5, "flood_index": 0.12, "route_congestion": 45 },
     "nonce": "8f4e2a",
     "hmac_signature": "a8b3f9d2c1..."
   }

CORE DELIVERABLES:
- Build a dark-mode, high-contrast, military command-center dashboard using React + TailwindCSS.
- Components to implement:
  1. `CommandMap.jsx`: Geospatial representation of Nagpur Regional Hospital, ICU power grids, and access corridors.
  2. `AuditLedger.jsx`: Live scrolling terminal-style feed displaying CPACF HMAC-SHA256 hashes locking incoming events.
  3. `RedAttackButton.jsx`: Clicking triggers `POST /api/simulate-attack`, causing the UI to flash `[HMAC AUTHENTICATION FAILED - INJECTION REJECTED]`.
  4. `EsgMetricCards.jsx`: Displays "CPU Energy Saved: 94.1% (Snap ML Gatekeeper avoids LLM spam)" and "Estimated Liability Avoided ($)".
- Provide a robust mock-data streaming toggle so the frontend can be demonstrated 100% offline if needed.
```

### 📋 Prompt for PAIR 2: Logic & Snap ML Engine
```markdown
You are the dedicated Machine Learning and Algorithm Engineer for Pair 2 on Project Syn (IBM Z Datathon 2026).
YOUR TERRITORY: `02-logic-engine/` ONLY.

STRICT ISOLATION CONSTRAINTS:
1. You MUST NOT touch React, HTML, CSS, or FastAPI server deployment.
2. You output standalone Python algorithms, data generators, and exported model artifacts (`.pmml` / `.pkl`) into `02-logic-engine/artifacts/`.
3. All telemetry payloads MUST strictly adhere to the Canonical Data Contract:
   {
     "packet_id": "SYN-xxxx",
     "timestamp": "ISO-8601",
     "sensor_location": "...",
     "metrics": { "grid_voltage": float, "flood_index": float, "route_congestion": int },
     "nonce": "hex_string",
     "hmac_signature": "sha256_hex"
   }

CORE DELIVERABLES:
- `data_generator.py`: Generates continuous high-throughput synthetic hospital & city sensor streams. Implements `sign_payload(secret_key)` using Python `hmac` and `hashlib.sha256`.
- `attack_injector.py`: Injects manipulated metrics with corrupted or forged signatures to demonstrate spoofing prevention.
- `train_snap_ml.py`: Trains a Random Forest Classifier to detect resource depletion anomalies. Exports model to PMML / cross-platform format compatible with IBM LinuxONE s390x.
- `routing_algorithm.py`: A deterministic graph solver (Dijkstra/Rules) that calculates safe ambulance corridors and ICU generator loads. THE LLM DOES NOT MAKE THE ROUTE DECISION; YOUR DETERMINISTIC SCRIPT DOES.
```

### 📋 Prompt for PAIR 3: Mainframe Core & Integration Leads
```markdown
You are the Chief Mainframe Architect & Backend Integration Lead for Pair 3 on Project Syn (IBM Z Datathon 2026).
YOUR TERRITORY: `03-mainframe-core/` ONLY.

STRICT ISOLATION CONSTRAINTS:
1. You own server orchestration, hardware-native integration, and deployment to the IBM LinuxONE (`s390x`) instance.
2. You connect Pair 2's logic models to the network and serve REST APIs to Pair 1's UI.
3. You enforce the Canonical Data Contract on all inbound and outbound streams.

CORE DELIVERABLES:
- `main.py`: FastAPI server exposing `/api/telemetry/ingest`, `/api/ledger/stream`, and `/api/simulate-attack`.
- `queue_worker.py`: Background worker utilizing `asyncio.Queue` to buffer rapid bursts of incoming telemetry, preventing SQLite `database is locked` concurrency exceptions.
- `hash_ledger.py`: Tamper-evident hash chain (`entry_i = HMAC(secret, prev_hash + payload + decision + timestamp)`). Incorporate terminology and hooks for IBM Z CPACF native acceleration.
- `llm_explainer.py`: Multi-lingual explainer (English, Hindi, Marathi) operating across 3 Sovereignty Modes:
  1. Connected: Cloud API / OpenRouter.
  2. Sovereign: Local Big-Endian compiled Phi-3 GGUF via llama.cpp on s390x.
  3. Degraded: Hardcoded deterministic emergency templates when offline.
- `telegram_dispatch.py`: Asynchronous webhook dispatcher routing briefs to field workers.
- `s390x_Miniconda_Setup.md`: Documented configuration guide for Miniconda on s390x, positioning this project as an open-source contribution to the IBM Z ecosystem.
```

---

## ⚡ Setup & Quickstart Commands

Run these terminal commands to initialize the complete repository and environment locally:

```bash
# 1. Clone or initialize the repository
git init Project-Syn-IBMZ
cd Project-Syn-IBMZ

# 2. Setup Pair 1 Frontend Workspace
cd 01-command-center
npm install
npm run dev

# 3. Setup Pair 2 Logic Engine Workspace (Separate Terminal)
cd ../02-logic-engine
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python data_generator.py

# 4. Setup Pair 3 Mainframe Core Workspace (Separate Terminal)
cd ../03-mainframe-core
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🏆 The Winning Narrative for Judges

> *"AegisCore didn't just route an ambulance. It authenticated incoming disaster telemetry at the edge, detected infrastructure failure via IBM Snap ML, calculated life-saving routes deterministically, and survived a simulated cyberattack and total internet blackout on an IBM LinuxONE mainframe without losing a single transaction. This is the definition of sovereign, trustworthy AI."*
