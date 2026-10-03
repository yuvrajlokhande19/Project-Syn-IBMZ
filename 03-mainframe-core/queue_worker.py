import asyncio
import logging
from typing import Optional

from hash_ledger import HashLedger
from telegram_dispatch import process_and_alert

# Create a queue with a maximum size to prevent memory exhaustion
_telemetry_queue: Optional[asyncio.Queue] = None
_worker_running = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_telemetry_queue() -> asyncio.Queue:
    global _telemetry_queue
    if _telemetry_queue is None:
        _telemetry_queue = asyncio.Queue(maxsize=10000)
    return _telemetry_queue

async def start_queue_worker():
    global _worker_running
    _worker_running = True
    queue = get_telemetry_queue()
    ledger = HashLedger()
    
    logger.info("Starting telemetry queue worker...")
    
    while _worker_running:
        try:
            # Wait for data with a timeout so we can periodically check _worker_running
            data = await asyncio.wait_for(queue.get(), timeout=1.0)
            
            try:
                # 1. Write to hash ledger
                ledger.record_telemetry(data)
                
                # 2. Check conditions and dispatch alerts if necessary
                await process_and_alert(data)
                
            except Exception as e:
                logger.error(f"Error processing telemetry data: {e}")
            finally:
                queue.task_done()
                
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break
            
    logger.info("Queue worker stopped.")

async def stop_queue_worker():
    global _worker_running
    _worker_running = False
