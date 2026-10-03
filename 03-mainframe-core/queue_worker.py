import asyncio
import sqlite3
import json
import logging
import os
import joblib
import pandas as pd
from hash_ledger import append_to_ledger
from telegram_dispatch import dispatch_alert, format_alert_message

logger = logging.getLogger(__name__)

QUEUE = asyncio.Queue()
DB_PATH = "telemetry.db"

# Load the Local Machine Learning Model (Random Forest trained on 10k sensors)
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '02-logic-engine', 'artifacts', 'anomaly_model.pkl')
try:
    ML_MODEL = joblib.load(MODEL_PATH)
    logger.info("Local Random Forest AI loaded successfully.")
except Exception as e:
    logger.warning(f"Could not load ML model: {e}")
    ML_MODEL = None

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
        
        # Write to Immutable Hash Ledger (CPACF Simulation)
        append_to_ledger(item)
        
        metrics = item.get('metrics', {})
        grid_voltage = metrics.get('grid_voltage', 220.0)
        flood_index = metrics.get('flood_index', 0.0)
        route_congestion = metrics.get('route_congestion', 0.0)
        
        is_anomaly = False
        anomaly_type = "NOMINAL"
        
        # 1. LOCAL ML INFERENCE (Analyzing Sensor Data)
        if ML_MODEL:
            df_infer = pd.DataFrame([[grid_voltage, flood_index, route_congestion]], 
                                    columns=['grid_voltage', 'flood_index', 'route_congestion'])
            prediction = ML_MODEL.predict(df_infer)
            if prediction[0] == 1:
                is_anomaly = True
                
        # 2. Rule-based specific overrides for demo scenarios
        if flood_index > 0.5:
            is_anomaly = True
            anomaly_type = "FLOOD"
        elif grid_voltage < 50.0:
            is_anomaly = True
            anomaly_type = "POWER_FAILURE"
        elif route_congestion == 100:
            is_anomaly = True
            anomaly_type = "EARTHQUAKE"
        elif route_congestion == 0 and item.get('metrics', {}).get('cctv_intel', {}).get('status') == "GREEN_CORRIDOR_ACTIVE":
            is_anomaly = True
            anomaly_type = "ORGAN_TRANSPLANT"
        elif item.get('metrics', {}).get('supply_chain', {}).get('blood_units_o_neg') == 0:
            is_anomaly = True
            anomaly_type = "RESOURCE_DEFICIT"

        if is_anomaly or item.get('status') == 'critical':
            # Trigger Dispatch Alert!
            msg = format_alert_message(item, anomaly_type, safe_route="Route B (Elevated)")
            dispatch_alert(msg)
            
    except Exception as e:
        logger.error(f"Failed to save to DB: {e}")

async def worker_task():
    init_db()
    logger.info("Queue worker started")
    while True:
        try:
            item = await QUEUE.get()
            await asyncio.to_thread(save_to_db, item)
            QUEUE.task_done()
        except asyncio.CancelledError:
            logger.info("Worker cancelled")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}")
