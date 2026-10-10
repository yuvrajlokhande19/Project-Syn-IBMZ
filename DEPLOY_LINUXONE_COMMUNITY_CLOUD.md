# 🚀 Project Syn // AegisCore: IBM LinuxONE (s390x) Deployment Guide

This guide details the exact steps to deploy and run **AegisCore** on the **IBM LinuxONE Community Cloud** (Ubuntu 22.04 LTS, Big-Endian `s390x` architecture, 4GB RAM).

---

## 🌐 1. IBM LinuxONE Community Cloud Access
- **Portal URL**: [IBM LinuxONE Community Cloud (Marist College)](https://linuxone.cloud.marist.edu/)
- **Instance Specifications**:
  - **OS**: Ubuntu 22.04 LTS
  - **Architecture**: `s390x` (IBM zSystems / LinuxONE)
  - **vCPUs**: 2 vCPUs
  - **RAM**: 4 GB (strictly managed with our swap allocation and lean process architecture)
  - **Disk**: 50 GB

---

## 🔑 2. SSH into your LinuxONE Instance
Open your terminal (PowerShell or Bash) and connect using your SSH private key:
```bash
ssh -i /path/to/your-key.pem linux1@<YOUR_LINUXONE_PUBLIC_IP>
```

---

## 📦 3. Transfer or Clone Code to LinuxONE

### Option A: Via GitHub (Recommended)
```bash
git clone https://github.com/yuvrajlokhande19/Project-Syn-IBMZ.git
cd Project-Syn-IBMZ
```

### Option B: Via SCP from Windows
From your local Windows PowerShell:
```powershell
scp -i "C:\path\to\your-key.pem" -r "c:\Users\lokha\Downloads\Project Syn" linux1@<YOUR_LINUXONE_PUBLIC_IP>:~/Project-Syn
```

---

## ⚡ 4. One-Command Automated Deployment

Inside your LinuxONE SSH session:
```bash
cd ~/Project-Syn/03-mainframe-core
chmod +x deploy_linuxone.sh
./deploy_linuxone.sh
```

### What this script automatically executes:
1. **Verifies Native s390x Architecture** (`uname -m`).
2. **Configures 2GB Swap Space** to prevent kernel Out-Of-Memory (OOM) crashes under high telemetry bursts.
3. **Installs System Dependencies** (`build-essential`, `libssl-dev`, `python3-venv`, `sqlite3`).
4. **Verifies CPACF Hardware Acceleration** using native OpenSSL.
5. **Sets up Python Virtual Environment** and installs lightweight dependencies (`fastapi`, `uvicorn`, `scikit-learn`, `joblib`, etc.).
6. **Initializes the SQLite CPACF Hash Ledger** (`ledger.db`).
7. **Runs Automated Regression Tests** (30/30 tests pass).

---

## 🛡️ 5. Configure Security Group / Firewall Port
In the **IBM LinuxONE Cloud Console**:
1. Navigate to **Access & Security** -> **Security Groups**.
2. Select your default security group and click **Manage Rules**.
3. Add Rule:
   - **Direction**: Ingress (Inbound)
   - **IP Protocol**: TCP
   - **Port**: `8000`
   - **Remote CIDR**: `0.0.0.0/0`
4. Click **Add**.

---

## 🚀 6. Launch Services in Production

### 1. Launch Mainframe Core API Gateway:
```bash
cd ~/Project-Syn/03-mainframe-core
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > aegiscore.log 2>&1 &
```

### 2. Launch Real-Time Sensor Simulator:
```bash
cd ~/Project-Syn/02-logic-engine
nohup python3 telemetry_simulator.py > simulator.log 2>&1 &
```

### 3. Verify Background Processes:
```bash
ps aux | grep -E "uvicorn|telemetry_simulator"
```

---

## 🖥️ 7. Accessing Live System & Demonstrating Features

- **Command Center Dashboard**: `http://<YOUR_LINUXONE_PUBLIC_IP>:8000/ui/`
- **Interactive OpenAPI Documentation**: `http://<YOUR_LINUXONE_PUBLIC_IP>:8000/docs`
- **Verify Cryptographic Chain**: `http://<YOUR_LINUXONE_PUBLIC_IP>:8000/api/ledger/verify`

### Demonstrating Zero-Trust Cyber Attacks on Stage:
Test the CPACF gate rejecting tampered telemetry in real time:
```bash
# 1. Payload Tampering Test (Returns HTTP 401)
curl -i -X POST http://127.0.0.1:8000/api/attack/simulate \
  -H "Content-Type: application/json" \
  -d '{"attack_type": "tamper"}'

# 2. Replay Attack Test (Returns HTTP 401)
curl -i -X POST http://127.0.0.1:8000/api/attack/simulate \
  -H "Content-Type: application/json" \
  -d '{"attack_type": "replay"}'

# 3. Sensor Spoofing Test (Returns HTTP 403)
curl -i -X POST http://127.0.0.1:8000/api/attack/simulate \
  -H "Content-Type: application/json" \
  -d '{"attack_type": "spoof"}'
```

---

## 🛑 8. Stopping Services
```bash
pkill -f "uvicorn"
pkill -f "telemetry_simulator.py"
```
