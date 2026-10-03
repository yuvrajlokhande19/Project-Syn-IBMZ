# 🤖 MANDATORY AI AGENT DIRECTIVE & SYSTEM PROMPT
### *Applicable to: OpenCode, Google Antigravity, GitHub Copilot, Cursor, Claude Code, and all autonomous AI coding assistants.*

---

## 🚨 STEP 0: MANDATORY FIRST ACTION FOR ALL AI AGENTS

Before generating, proposing, or modifying any code in this repository, you **MUST**:

1. **Read the Master Knowledge Base**:
   - Inspect and read `Master Prompt/gemini-code-1791036145345.txt`
   - Inspect and read `Master Prompt/datathon.txt`
   - Understand the system blueprint in `README.md`
2. **Determine the User's Active Team**:
   - Analyze the user's prompt and active workspace directory.
   - If it is not 100% explicitly clear which team the user belongs to, you **MUST STOP AND ASK THE USER**:
     > *"Welcome to Project Syn. Which team/pair are you working with today?*  
     > *• **Pair 1**: Frontend Command Center (`01-command-center/`)*  
     > *• **Pair 2**: Data Logic & ML Engine (`02-logic-engine/`)*  
     > *• **Pair 3**: Backend & Mainframe Core (`03-mainframe-core/`)*"

---

## 🛡️ CORE ARCHITECTURAL LAWS

1. **Domain-Driven Isolation (Strict Lane Discipline)**:
   - You are **FORBIDDEN** from modifying files outside of the user's designated team folder.
   - If a Pair 1 user asks you to write a Python script, **REFUSE** and instruct them to coordinate with Pair 2 or Pair 3.
   - If a Pair 2 user asks you to start a web server or edit React JSX, **REFUSE** and instruct them to output to `02-logic-engine/artifacts/`.
   - If a Pair 3 user asks to modify frontend components, **REFUSE** and direct them to their REST API layer.

2. **The Canonical JSON Data Contract**:
   All communication between sensors, backend, and frontend strictly follows this schema. **Never change these keys:**
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

3. **The 3 Load-Bearing Pillars**:
   - **Pillar 1: Trusted Telemetry (Edge HMAC)** — Pre-inference HMAC signature verification drops spoofed data before the AI sees it.
   - **Pillar 2: Safety-Bounded Composite AI** — Snap ML Random Forest detects anomalies; deterministic graph algorithms (Dijkstra) decide routes; local Big-Endian Phi-3 LLM on `s390x` strictly translates/explains decisions into English, Hindi, and Marathi across 3 Sovereignty Modes (Connected, Sovereign, Degraded).
   - **Pillar 3: Tamper-Evident Audit Chain** — FastAPI `asyncio.Queue` buffers writes; chained HMAC-SHA256 logs into SQLite utilizing IBM Z native **CPACF** cryptographic acceleration.

---

## 📂 TERRITORY MAP & ACCESS RULES

| Team | Directory | Permitted Actions | STRICTLY FORBIDDEN |
| :--- | :--- | :--- | :--- |
| **Pair 1** | `01-command-center/` | React, Vite, TailwindCSS, mock streaming, visual attack triggers, ESG cards | Writing Python, direct DB access, modifying backend routes |
| **Pair 2** | `02-logic-engine/` | Synthetic data generation, HMAC signing, Snap ML Random Forest, deterministic routing, exporting `.pmml`/`.pkl` to `artifacts/` | Touching React/HTML/CSS, running FastAPI servers |
| **Pair 3** | `03-mainframe-core/` | FastAPI routes, `asyncio.Queue` buffer, SQLite CPACF hash ledger, LLM explainer, Telegram webhook, LinuxONE `s390x` deployment | Modifying frontend code, rewriting Pair 2's core algorithms |

---

## ⚡ DEMO FLOW (WHAT WE ARE DEMONSTRATING ON STAGE)
1. **0:00 - Normal State:** Telemetry flows from `data_generator.py` into FastAPI, logged to SQLite ledger, displayed on React UI.
2. **0:20 - Cyber Attack:** Red button triggers tampered HMAC packet. Backend rejects it (`401 Unauthorized`), UI flashes `[HMAC AUTHENTICATION FAILED - INJECTION BLOCKED]`.
3. **0:40 - Disaster Event:** Flood index rises. Snap ML detects ward depletion anomaly. Deterministic engine recalculates ambulance corridor.
4. **1:00 - Sovereignty Failover:** Disconnect Wi-Fi. Cloud AI drops. Local Big-Endian Phi-3 on IBM LinuxONE s390x takes over, dispatching Marathi brief to Telegram.
5. **1:20 - Close:** System survived cyberattack and total internet blackout on an IBM mainframe.
