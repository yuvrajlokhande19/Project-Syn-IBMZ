#!/bin/bash
export PATH="$PATH:/home/linux1/.local/bin"
echo "[1/5] Stopping stale processes..."
screen -X -S api quit 2>/dev/null || true
screen -X -S sim quit 2>/dev/null || true
screen -X -S tunnel quit 2>/dev/null || true
screen -X -S tunnel2 quit 2>/dev/null || true
pkill -f uvicorn 2>/dev/null || true
pkill -f telemetry_simulator 2>/dev/null || true
pkill -f 'ssh.*pinggy' 2>/dev/null || true
pkill -f 'ssh.*localhost.run' 2>/dev/null || true
sleep 2

echo "[2/5] Starting FastAPI Mainframe Core on 0.0.0.0:8000..."
screen -dmS api bash -c 'export PATH="$PATH:/home/linux1/.local/bin" && cd /home/linux1/Project-Syn-IBMZ/03-mainframe-core && uvicorn main:app --host 0.0.0.0 --port 8000 > /home/linux1/api.log 2>&1'
sleep 3

echo "[3/5] Starting Edge Telemetry Simulator..."
screen -dmS sim bash -c 'export PATH="$PATH:/home/linux1/.local/bin" && cd /home/linux1/Project-Syn-IBMZ && python3 02-logic-engine/telemetry_simulator.py > /home/linux1/sim.log 2>&1'
sleep 1

echo "[4/5] Starting Public Tunnels (Pinggy and Localhost.run)..."
> /home/linux1/pinggy.log
> /home/linux1/localhost_run.log

screen -dmS tunnel bash -c 'while true; do ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 a.pinggy.io 2>&1 | tee /home/linux1/pinggy.log; sleep 5; done'
screen -dmS tunnel2 bash -c 'while true; do ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run 2>&1 | tee /home/linux1/localhost_run.log; sleep 5; done'

echo "[5/5] Waiting for public tunnel URLs to negotiate..."
sleep 6

echo "================ PRODUCTION STATUS ================"
curl -s http://127.0.0.1:8000/api/system/health
echo ""
echo "--- Pinggy URL ---"
grep -oE 'https://[a-zA-Z0-9.-]+\.(run\.pinggy-free\.link|free\.pinggy\.net)' /home/linux1/pinggy.log | head -n 2
echo "--- Localhost.run URL ---"
grep -oE 'https://[a-zA-Z0-9.-]+\.lhr\.life' /home/linux1/localhost_run.log | head -n 1
echo "==================================================="
