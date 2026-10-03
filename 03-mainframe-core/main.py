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
