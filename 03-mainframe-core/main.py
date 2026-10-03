import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from queue_worker import start_queue_worker, get_telemetry_queue, stop_queue_worker
from hash_ledger import HashLedger
import hmac
import hashlib
import json
import contextlib

SECRET_KEY = b"mainframe_secret_key"

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # init db
    HashLedger()
    worker_task = asyncio.create_task(start_queue_worker())
    yield
    await stop_queue_worker()
    worker_task.cancel()

app = FastAPI(title="Project Syn Mainframe Core", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/telemetry/ingest")
async def ingest_telemetry(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    expected_signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
    
    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    queue = get_telemetry_queue()
    try:
        queue.put_nowait(data)
    except asyncio.QueueFull:
        raise HTTPException(status_code=503, detail="Queue is full, try again later")
    
    return {"status": "success", "message": "Telemetry accepted for processing"}

import sqlite3

@app.get("/api/telemetry/live")
async def get_live_telemetry():
    """Endpoint for Pair 1 Dashboard to fetch live data from the IBM Mainframe"""
    try:
        # Fetch the latest 10 verified blocks from the Hash Ledger
        with sqlite3.connect("ledger.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, payload, hash FROM telemetry_ledger ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            
            latest_data = []
            for row in rows:
                latest_data.append({
                    "timestamp": row["timestamp"],
                    "hash": row["hash"],
                    "data": json.loads(row["payload"])
                })
                
            # Fetch latest alert
            cursor.execute("SELECT timestamp, location, message FROM alerts ORDER BY id DESC LIMIT 1")
            alert_row = cursor.fetchone()
            latest_alert = None
            if alert_row:
                latest_alert = {
                    "timestamp": alert_row["timestamp"],
                    "location": alert_row["location"],
                    "message": alert_row["message"]
                }
                
        return {"status": "success", "live_stream": latest_data, "latest_alert": latest_alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
