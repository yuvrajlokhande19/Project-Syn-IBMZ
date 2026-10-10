@echo off
echo =========================================================
echo Starting Project Syn Mainframe Core (LinuxONE s390x Emulation)
echo =========================================================

echo [1/3] Checking dependencies...
pip install -r requirements.txt

echo [2/3] Initializing CPACF Chained Hash Ledger Database...
python -c "from hash_ledger import init_ledger_db; init_ledger_db()"

echo [3/3] Starting FastAPI Mainframe Server on Port 8000...
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
