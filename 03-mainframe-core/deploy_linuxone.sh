#!/bin/bash
# ==============================================================================
# PROJECT SYN // AEGISCORE - IBM LINUXONE (s390x) CLOUD DEPLOYMENT SCRIPT
# Target: Ubuntu 22.04 LTS on IBM LinuxONE Community Cloud (Marist College)
# Architecture: Big-Endian s390x / 4GB RAM ceiling
# ==============================================================================

set -e

echo "================================================================================"
echo "    AEGISCORE // IBM LinuxONE (s390x) Production Deployment"
echo "================================================================================"

ARCH=$(uname -m)
echo "[INFO] Detected System Architecture: $ARCH"
if [ "$ARCH" != "s390x" ]; then
    echo "[WARN] Not running on native s390x architecture. Emulation mode active."
fi

# 1. Memory Discipline & Swap Configuration (Prevents OOM on 4GB instances)
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
echo "[INFO] Total System Memory: ${TOTAL_MEM}MB"
if [ "$TOTAL_MEM" -le 4500 ] && [ ! -f /swapfile ]; then
    echo "[STEP 1/6] Allocating 2GB Swap Space to safeguard 4GB RAM boundary..."
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "       Swap created and activated successfully."
fi

# 2. System Packages Installation
echo "[STEP 2/6] Installing Ubuntu packages and OpenSSL CPACF dependencies..."
sudo apt-get update -y
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    git \
    net-tools

# 3. CPACF Hardware Crypto Acceleration Verification
echo "[STEP 3/6] Verifying OpenSSL CPACF hardware acceleration..."
openssl speed sha256 2>&1 | head -n 4 || true

# 4. Python Virtual Environment Setup
echo "[STEP 4/6] Setting up Python virtual environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 5. Cryptographic Ledger Initialization
echo "[STEP 5/6] Initializing CPACF SQLite Hash Ledger..."
python3 -c "from hash_ledger import init_ledger_db; init_ledger_db(); print('       Ledger DB initialized successfully.')"

# 6. Self-Test Suite Verification
echo "[STEP 6/6] Executing Automated Regression & Zero-Trust Suite..."
python3 test_suite.py

echo "================================================================================"
echo "✅ AEGISCORE DEPLOYMENT READY ON IBM LINUXONE (s390x)!"
echo "================================================================================"
echo "To run the production server in the background:"
echo "  cd $SCRIPT_DIR"
echo "  source venv/bin/activate"
echo "  nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > aegiscore.log 2>&1 &"
echo ""
echo "To stream live sensor telemetry into the CPACF gate:"
echo "  cd $SCRIPT_DIR/../02-logic-engine"
echo "  nohup python3 telemetry_simulator.py > simulator.log 2>&1 &"
echo ""
echo "Access Dashboard at: http://<YOUR_LINUXONE_PUBLIC_IP>:8000/ui/"
echo "================================================================================"
