# 03-mainframe-core (PAIR 3 ONLY)

## Strict Rules
- **Stack:** Python, FastAPI, Uvicorn, SQLite3, asyncio, requests/httpx.
- **Role:** High-concurrency ingestion server, CPACF-accelerated hash ledger, Big-Endian LLM failover, Telegram dispatch, IBM LinuxONE s390x deployment.
- **Strict Boundary:** The only team deploying to the s390x server. Ingests Pair 2's model/algorithms and exposes REST endpoints for Pair 1.

## Target Files
- `main.py` (FastAPI application and REST routes)
- `queue_worker.py` (asyncio.Queue shock-absorber for SQLite writes)
- `hash_ledger.py` (Tamper-evident HMAC-SHA256 audit ledger)
- `llm_explainer.py` (3 Sovereignty Modes: Cloud, Local Big-Endian Phi-3, Degraded templates)
- `telegram_dispatch.py` (Multi-lingual EN/HI/MR webhook dispatcher)
- `s390x_Miniconda_Setup.md` (Deployment documentation)
