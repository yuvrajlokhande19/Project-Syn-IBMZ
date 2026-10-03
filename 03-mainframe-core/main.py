import asyncio
import hmac
import hashlib
from fastapi import FastAPI, HTTPException, Request, Depends
from contextlib import asynccontextmanager
from typing import Dict, Any

from queue_worker import start_queue_worker, stop_queue_worker, get_telemetry_queue

# In a real system, this would be stored securely (e.g., AWS Secrets Manager, HashiCorp Vault)
SECRET_KEY = b"mainframe_secret_key"

def verify_hmac(body: bytes, signature: str) -> bool:
    if not signature:
        return False
    expected_signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background queue worker
    worker_task = asyncio.create_task(start_queue_worker())
    yield
    # Shutdown: Stop the background queue worker
    await stop_queue_worker()
    await worker_task

app = FastAPI(title="Mainframe Core API", lifespan=lifespan)

@app.post("/api/telemetry/ingest")
async def ingest_telemetry(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Signature")
    
    if not verify_hmac(body, signature):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
        
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    queue = get_telemetry_queue()
    try:
        queue.put_nowait(data)
    except asyncio.QueueFull:
        raise HTTPException(status_code=503, detail="Queue is full, try again later")
        
    return {"status": "success", "message": "Telemetry accepted for processing"}
