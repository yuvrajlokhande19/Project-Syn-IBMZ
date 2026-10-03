#!/bin/bash
# ==============================================================================
# PROJECT SYN - IBM LINUXONE (s390x) CLOUD DEPLOYMENT SCRIPT
# Run this script on your IBM LinuxONE instance to install all dependencies.
# ==============================================================================

set -e

echo "[1/4] Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv sqlite3 build-essential libssl-dev libffi-dev python3-dev

echo "[2/4] Setting up Python Virtual Environment..."
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate

echo "[3/4] Installing Python Backend Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/4] Initializing CPACF SQLite Ledger Database..."
# Run a quick python command to initialize the ledger
python -c "from hash_ledger import HashLedger; HashLedger()"

echo "====================================================================="
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "To start the Mainframe Core API in the background on port 8000:"
echo "  source venv/bin/activate"
echo "  nohup uvicorn main:app --host 0.0.0.0 --port 8000 &"
echo "====================================================================="
