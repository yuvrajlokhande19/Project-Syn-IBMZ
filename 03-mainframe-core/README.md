# ⚡ 03-mainframe-core | Pair 3 Territory (Backend & Mainframe Core)
### *FastAPI Ingestion, asyncio.Queue Shock Absorber, CPACF Hash Ledger & LinuxONE Deployment*

---

## 🔒 STRICT TERRITORY & SYSTEM BOUNDARIES
> **LOCKED BOUNDARY**: You are strictly confined to `03-mainframe-core/`.  
> **LEADERSHIP RESPONSIBILITIES**:
> - ✅ You own the bridge connecting Pair 2's algorithms to Pair 1's UI.
> - ✅ You are the ONLY pair deploying to the IBM LinuxONE (`s390x`) virtual machine.
> - ❌ You DO NOT modify frontend React components.
> - ❌ You DO NOT rewrite Pair 2's core algorithms; you ingest their exported models from `02-logic-engine/artifacts/`.

---

## 🤖 AI AGENT DIRECTIVE (If you are an AI assistant in this folder)
If an AI coding assistant (OpenCode, Antigravity, Copilot, etc.) is operating inside this folder:
1. **First Action:** Read `../Master Prompt/gemini-code-1791036145345.txt` and `../README.md` to understand the full system.
2. **Refusal Law:** If the user asks you to write frontend UI code, refuse and redirect them to Pair 1 (`01-command-center`).
3. **Primary Duty:** Implement the high-concurrency FastAPI server, `asyncio.Queue` write buffer to prevent SQLite database locks, CPACF HMAC-SHA256 audit ledger, 3 Modes of Sovereignty (Cloud, Local Big-Endian Phi-3, Degraded), Telegram webhook, and LinuxONE s390x configuration.

---

## 📜 Canonical Data Contract
Your `/api/telemetry/ingest` endpoint accepts and validates this exact payload:
```json
{
  "packet_id": "SYN-1",
  "timestamp": "2026-10-03T18:58:28Z",
  "sensor_location": "Nagpur_Central_ICU",
  "metrics": {
    "grid_voltage": 220,
    "flood_index": 0.12,
    "route_congestion": 45
  },
  "nonce": "8f4e2a",
  "hmac_signature": "hash"
}
```

---

## 🎯 Deliverables & Scripts
1. **`main.py`**:
   - Exposes `POST /api/telemetry/ingest`, `GET /api/ledger/stream`, and `POST /api/simulate-attack`.
   - Validates incoming `hmac_signature` before allowing payload past the edge.
2. **`queue_worker.py`**:
   - Implements an `asyncio.Queue` shock absorber. Catches burst telemetry in memory and writes sequentially to `syn_ledger.db`, eliminating `sqlite3.OperationalError: database is locked`.
3. **`hash_ledger.py`**:
   - Tamper-evident cryptographic audit chain (`entry_i = HMAC(secret, prev_hash + payload + decision + timestamp)`).
   - Designed to exploit IBM Z's native **CPACF** (Central Processor Assist for Cryptographic Functions).
4. **`llm_explainer.py`**:
   - Manages the **3 Modes of Sovereignty**:
     - *Connected Mode:* OpenRouter Cloud API.
     - *Sovereign Mode:* Local Big-Endian compiled Phi-3 GGUF via llama.cpp on `s390x` (zero cloud dependency).
     - *Degraded Mode:* Deterministic rule-based emergency templates when all LLMs are offline.
5. **`telegram_dispatch.py`**:
   - Asynchronously dispatches emergency briefs in English, Hindi, and Marathi to field responders.
6. **`s390x_Miniconda_Setup.md`**:
   - Setup guide documenting Miniconda on s390x LinuxONE, satisfying the Datathon's Open-Source contribution bonus.

---

## ⚡ Active Kanban Ticket
- **Issue #3**: [[BE-01] Build FastAPI Ingest Server with Async Queue Shock-Absorber and HMAC Validator](https://github.com/yuvrajlokhande19/Project-Syn-IBMZ/issues/3)
