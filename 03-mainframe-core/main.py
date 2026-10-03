import asyncio
import hashlib
import hmac
import logging
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from contextlib import asynccontextmanager

from queue_worker import worker_task, QUEUE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
SECRET_KEY = b"super_secret_syn_key"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background queue worker
    worker = asyncio.create_task(worker_task())
    yield
    # Shutdown
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan, title="Project Syn - Mainframe Core Telemetry API")

class TelemetryPayload(BaseModel):
    device_id: str
    timestamp: float
    data: dict

async def verify_hmac(request: Request):
    signature = request.headers.get("X-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    body = await request.body()
    expected_signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return True

@app.post("/api/telemetry/ingest")
async def ingest_telemetry(payload: TelemetryPayload, verified: bool = Depends(verify_hmac)):
    """
    Ingests telemetry data, validates HMAC, and puts it in the async queue for processing.
    """
    # Put data in queue
    try:
        await QUEUE.put(payload.model_dump())
        logger.info(f"Received valid telemetry from {payload.device_id}")
        return {"status": "success", "message": "Telemetry queued for processing"}
    except Exception as e:
        logger.error(f"Error queueing telemetry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
