import asyncio
import sqlite3
import json
import logging
from hash_ledger import append_to_ledger
from telegram_dispatch import dispatch_alert

logger = logging.getLogger(__name__)

QUEUE = asyncio.Queue()
DB_PATH = "telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id TEXT NOT NULL,
            timestamp REAL NOT NULL,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(item):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO telemetry (packet_id, timestamp, data) VALUES (?, ?, ?)",
            (item['packet_id'], item['unix_timestamp'], json.dumps(item))
        )
        conn.commit()
        conn.close()
        
        # Also write to hash ledger
        append_to_ledger(item)
        
        # Check for anomalies and alert (example logic)
        if item.get('status') == 'critical':
            dispatch_alert(f"Critical anomaly detected for sensor {item['sensor_location']}")
            
    except Exception as e:
        logger.error(f"Failed to save to DB: {e}")

async def worker_task():
    init_db()
    logger.info("Queue worker started")
    while True:
        try:
            item = await QUEUE.get()
            # Offload blocking DB operations to a thread
            await asyncio.to_thread(save_to_db, item)
            QUEUE.task_done()
        except asyncio.CancelledError:
            logger.info("Worker cancelled")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}")
