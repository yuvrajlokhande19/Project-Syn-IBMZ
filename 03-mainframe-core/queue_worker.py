"""
================================================================================
Project Syn / AegisCore: Mainframe Telemetry Asynchronous Queue Worker
Hardware Target: IBM LinuxONE s390x (CPACF Acceleration Architecture)
================================================================================
Consumes verified telemetry from the asynchronous shock-absorber queue.
- Computes Snap ML / Random Forest AI cross-sensor inference.
- Implements Dijkstra deterministic hospital rerouting (NagpurHospitalRouter).
- Monitored supply chain checks (Diesel < 4h reorder, O-Neg Blood broadcast, Organ transport).
- Writes verified packets to the immutable CPACF ledger.
- Dispatches trilingual emergency alerts.
================================================================================
"""

import os
import asyncio
import logging
import json
from collections import deque
from typing import Dict, Any, List, Optional
try:
    import pandas as pd
except ImportError:
    pd = None

from hash_ledger import append_to_ledger, log_alert
from telegram_dispatch import dispatch_alert, format_alert_message
from routing_algorithm import NagpurHospitalRouter
from local_ai_orchestrator import LOCAL_AI_AGENT

logger = logging.getLogger("queue_worker")
logger.setLevel(logging.INFO)

# Asynchronous shock-absorber ingestion queue
QUEUE: asyncio.Queue = asyncio.Queue()

# In-memory circular buffer of recently verified telemetry blocks for ultra-low latency live UI
MAX_LIVE_BUFFER = 100
LIVE_BUFFER: deque = deque(maxlen=MAX_LIVE_BUFFER)

# Attempt to load Random Forest AI trained on 10,000 sensor matrices
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '02-logic-engine', 'artifacts', 'anomaly_model.pkl')
ML_MODEL = None
try:
    if os.path.exists(MODEL_PATH):
        import joblib
        ML_MODEL = joblib.load(MODEL_PATH)
        logger.info(f"[SNAP ML] Random Forest model loaded successfully from {MODEL_PATH}")
    else:
        logger.warning(f"[SNAP ML] Model artifact not found at {MODEL_PATH}. Using deterministic heuristic engine.")
except Exception as e:
    logger.warning(f"[SNAP ML] Could not load ML model: {e}. Fallback to deterministic rules active.")
    ML_MODEL = None


def compute_safe_route(anomaly_type: str, sensor_location: str) -> str:
    """
    Invokes the deterministic NagpurHospitalRouter (Dijkstra's Shortest Path)
    to dynamically recalculate safe ambulance corridors around disaster zones.
    """
    router = NagpurHospitalRouter()
    valid_nodes = list(router.graph.keys())

    # Map sensor location to known hospital node if matching
    incident_node = sensor_location if sensor_location in valid_nodes else "GMC_Nagpur"

    # In case of flooding or severe damage, penalize routes through the incident area
    if anomaly_type in ("FLOOD", "EARTHQUAKE"):
        router.update_weights(incident_node, penalty=999)

    # Route towards closest alternate critical facility
    target_node = "AIIMS_Nagpur" if incident_node != "AIIMS_Nagpur" else "Mayo_Hospital"

    try:
        path, cost = router.dijkstra(incident_node, target_node)
        if path and cost < float("inf"):
            return f"{' -> '.join(path)} (Transit Weight: {cost})"
    except Exception as e:
        logger.error(f"[ROUTER ERROR] Dijkstra calculation failed: {e}")

    return "Corridor Wardha Road (Elevated Expressway)"


def process_packet(item: Dict[str, Any]):
    """
    Synchronous processing core executed within threadpool:
    1. Runs ML & physical heuristic anomaly checks.
    2. Runs supply chain life-safety monitors.
    3. Persists to CPACF chained ledger.
    4. Triggers emergency trilingual dispatch if required.
    """
    try:
        # Extract metrics
        metrics = item.get("metrics", {})
        grid_voltage = float(metrics.get("grid_voltage", 220.0))
        flood_index = float(metrics.get("flood_index", 0.0))
        route_congestion = float(metrics.get("route_congestion", 40.0))
        supply_chain = metrics.get("supply_chain", {})
        cctv_intel = metrics.get("cctv_intel", {})

        is_anomaly = False
        anomaly_type = "NOMINAL"
        anomaly_reasons: List[str] = []

        # -------------------------------------------------------------
        # STEP 1: AI INFERENCE (IBM Snap ML / Random Forest)
        # -------------------------------------------------------------
        if ML_MODEL is not None:
            try:
                if pd is not None:
                    df_infer = pd.DataFrame(
                        [[grid_voltage, flood_index, route_congestion]],
                        columns=['grid_voltage', 'flood_index', 'route_congestion']
                    )
                    prediction = ML_MODEL.predict(df_infer)
                else:
                    prediction = ML_MODEL.predict([[grid_voltage, flood_index, route_congestion]])
                if prediction[0] == 1:
                    is_anomaly = True
                    anomaly_reasons.append("ML_CLASSIFIER_ANOMALY")
            except Exception as ml_err:
                logger.debug(f"[ML INFERENCE NOTICE] {ml_err}")

        # -------------------------------------------------------------
        # STEP 2: DETERMINISTIC EMERGENCY RULES & PHYSICS OVERRIDES
        # -------------------------------------------------------------
        if flood_index > 0.5:
            is_anomaly = True
            anomaly_type = "FLOOD"
            anomaly_reasons.append(f"Flood index critical ({flood_index:.2f})")
        elif grid_voltage < 50.0:
            is_anomaly = True
            anomaly_type = "POWER_FAILURE"
            anomaly_reasons.append(f"Grid voltage collapse ({grid_voltage:.1f}V)")
        elif route_congestion >= 98:
            is_anomaly = True
            anomaly_type = "EARTHQUAKE"
            anomaly_reasons.append("Extreme grid congestion / structural failure")
        elif cctv_intel.get("status") == "STRUCTURAL_DAMAGE":
            is_anomaly = True
            anomaly_type = "EARTHQUAKE"
            anomaly_reasons.append("CCTV confirmed structural damage")

        # -------------------------------------------------------------
        # STEP 3: SUPPLY CHAIN & LIFE SAFETY MONITORS
        # -------------------------------------------------------------
        # A. Generator Diesel: < 4 hours triggers automated fuel replenishment
        diesel_fuel = supply_chain.get("diesel_fuel_liters", 3000)
        # Average ICU generator burns ~100L/hour. < 400L represents < 4 hours reserve.
        if diesel_fuel < 400 or supply_chain.get("diesel_hours_left", 24) < 4.0:
            is_anomaly = True
            anomaly_type = "DIESEL_LOW"
            anomaly_reasons.append(f"Diesel reserves critical ({diesel_fuel}L remaining, < 4 hours)")

        # B. Blood Supply: 0 or depleted O-Neg triggers IoT radio broadcast to civilian taxi swarm
        blood_o_neg = supply_chain.get("blood_units_o_neg")
        if blood_o_neg is not None and blood_o_neg <= 0:
            is_anomaly = True
            anomaly_type = "RESOURCE_DEFICIT"
            anomaly_reasons.append("Zero units of O-Negative emergency blood in bank")

        # C. Organ Transport: Active heart match triggers Green Corridor & insurance claim
        if (
            supply_chain.get("organ_match") == "HEART_VIABLE"
            or cctv_intel.get("status") == "GREEN_CORRIDOR_ACTIVE"
            or item.get("status") == "organ_transport"
        ):
            is_anomaly = True
            anomaly_type = "ORGAN_TRANSPLANT"
            anomaly_reasons.append("Heart donor viable - Green Corridor priority active")

        # Honor critical status flag from payload
        if item.get("status") == "critical" and anomaly_type == "NOMINAL":
            is_anomaly = True
            anomaly_type = "GENERAL_CRITICAL"

        # Execute Autonomous Local AI Orchestrator (100% on-premise s390x)
        try:
            local_ai_eval = LOCAL_AI_AGENT.evaluate_telemetry(item)
            item["local_ai"] = local_ai_eval
        except Exception as ai_err:
            logger.debug(f"[LOCAL AI NOTICE] {ai_err}")

        # -------------------------------------------------------------
        # STEP 4: WRITE TO IMMUTABLE CPACF HASH LEDGER
        # -------------------------------------------------------------
        chained_hash = append_to_ledger(item, verified_cpacf=1)
        item["ledger_hash"] = chained_hash

        # Update circular live buffer for instantaneous dashboard reads
        LIVE_BUFFER.append({
            "hash": chained_hash,
            "data": item,
            "timestamp": item.get("timestamp")
        })

        # -------------------------------------------------------------
        # STEP 5: EMERGENCY ROUTING & TRILINGUAL DISPATCH
        # -------------------------------------------------------------
        if is_anomaly:
            location = item.get("sensor_location", "Nagpur Metro Emergency Center")
            safe_route = compute_safe_route(anomaly_type, location)
            extra_context = "; ".join(anomaly_reasons)

            # Generate Trilingual Dispatch Message
            alert_msg = format_alert_message(
                data=item,
                anomaly_type=anomaly_type,
                safe_route=safe_route,
                extra_context=extra_context
            )

            # Log to SQLite alerts table
            network_mode = item.get("network_mode", "satellite_api")
            log_alert(location, anomaly_type, alert_msg, network_mode)

            # Transmit to Telegram and console
            dispatch_alert(alert_msg)

    except Exception as e:
        logger.error(f"[QUEUE WORKER ERROR] Failed to process telemetry packet: {e}", exc_info=True)


async def worker_task():
    """Background consumer loop pulling packets off the async queue."""
    logger.info("[QUEUE WORKER] Ingestion queue consumer started.")
    while True:
        try:
            item = await QUEUE.get()
            # Offload heavy cryptographic and DB operations to threadpool
            await asyncio.to_thread(process_packet, item)
            QUEUE.task_done()
        except asyncio.CancelledError:
            logger.info("[QUEUE WORKER] Background consumer shutting down.")
            break
        except Exception as e:
            logger.error(f"[QUEUE WORKER EXCEPTION] Unexpected error: {e}")
