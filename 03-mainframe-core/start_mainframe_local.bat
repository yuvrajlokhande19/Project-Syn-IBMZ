@echo off
echo =========================================================
echo Starting Project Syn Mainframe Core (Local Testing)
echo =========================================================

echo [1/3] Checking dependencies...
pip install -r requirements.txt

echo [2/3] Initializing Database...
python -c "from hash_ledger import HashLedger; HashLedger()"

echo [3/3] Starting FastAPI Server on Port 8001...
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
