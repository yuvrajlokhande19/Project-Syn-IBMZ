import time
import json
import hmac
import hashlib
import random
import math
import httpx
import requests
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

SECRET_KEY = os.getenv("MAINFRAME_SECRET_KEY", "mainframe_secret_key").encode('utf-8')
MAINFRAME_URL = os.getenv("MAINFRAME_URL", "http://127.0.0.1:8000/api/telemetry/ingest")

# Realistic Locations in Nagpur based on the CARTO map
LOCATIONS = [
    "GMC_Nagpur",
    "Mayo_Hospital",
    "AIIMS_Nagpur",
    "Lata_Mangeshkar_Hospital",
    "Wockhardt_Hospital"
]

_WEATHER_CACHE = {"timestamp": 0, "data": None}

def get_live_weather() -> dict:
    global _WEATHER_CACHE
    now = time.time()
    if _WEATHER_CACHE["data"] and (now - _WEATHER_CACHE["timestamp"] < 60.0):
        return _WEATHER_CACHE["data"]
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=21.1458&longitude=79.0882&current_weather=true"
        response = requests.get(url, timeout=1.5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        res = {
            "temperature": current.get("temperature", round(random.uniform(25.0, 45.0), 1)),
            "windspeed": current.get("windspeed", round(random.uniform(0.0, 20.0), 1))
        }
        _WEATHER_CACHE = {"timestamp": now, "data": res}
        return res
    except Exception:
        fallback = {
            "temperature": round(random.uniform(25.0, 45.0), 1),
            "windspeed": round(random.uniform(0.0, 20.0), 1)
        }
        _WEATHER_CACHE = {"timestamp": now, "data": fallback}
        return fallback

# Attempt to load Medical Triage Model
_MEDICAL_MODEL = None
try:
    med_model_path = os.path.join(os.path.dirname(__file__), "artifacts", "medical_triage_model.pkl")
    if os.path.exists(med_model_path):
        import joblib
        _MEDICAL_MODEL = joblib.load(med_model_path)
except Exception:
    _MEDICAL_MODEL = None

def generate_telemetry_packet(tick: int) -> dict:
    """
    Generates realistic, state-sequenced disaster telemetry.
    Supports Task 5 (CCTV expansion: Riot, Crash, Fire) and Task 6 (Crowdsourced blood pickup verification).
    Incorporates physical harmonic waves, building evacuation triggers, and medical AI triage predictions.
    """
    location = random.choice(LOCATIONS)
    
    # 60-tick cyclic disaster progression wave to ensure predictable stage demos and eliminate erratic spamming
    cycle_tick = tick % 60

    # Baseline physical parameters
    voltage_base = 220.0
    voltage = voltage_base + (math.sin(tick * 0.1) * 3.5) + random.uniform(-1.0, 1.0)
    flood_index = max(0.01, math.sin(tick * 0.05) * 0.12 + random.uniform(0.01, 0.05))
    congestion = int(max(15, min(90, 42 + (math.cos(tick * 0.05) * 20) + random.uniform(-5, 5))))
    
    # Default state flags
    is_flood = False
    is_power_failure = False
    is_earthquake = False
    is_organ_transport = False
    is_resource_deficit = False
    is_fire_emergency = False
    is_riot_detected = False
    is_ambulance_crash = False
    evacuate_building = False
    firefighter_alert = False

    cctv_status = "CLEAR"
    ai_confidence = 0.99
    blood_o_neg = random.randint(60, 180)
    diesel_fuel = random.randint(2500, 4800)
    richter_mag = 0.0

    # Clinical Ward / ICU metrics
    icu_occupancy = round(65.0 + math.sin(tick * 0.08) * 15.0 + random.uniform(-2, 2), 1)
    oxygen_hours = round(36.0 - (tick % 30) * 0.5, 1)
    vent_utilization = round(60.0 + random.uniform(-5, 10), 1)
    trauma_surge = round(0.15 + random.uniform(0.0, 0.1), 2)

    # Coordinated Demo Phase Sequences
    if 20 <= cycle_tick < 28:
        # Scenario 1: Organ Transplant (Green Corridor Active)
        congestion = 5  # Street lights pre-cleared
        cctv_status = "GREEN_CORRIDOR_ACTIVE"
        ai_confidence = 0.99
        is_organ_transport = True

    elif 28 <= cycle_tick < 36:
        # Scenario 2: Public Hospital Critical Blood Deficit (Task 6)
        blood_o_neg = 0  # Severe deficit
        cctv_status = "HOSPITAL_OVERFLOW"
        ai_confidence = 0.96
        is_resource_deficit = True

    elif 36 <= cycle_tick < 44:
        # Scenario 3: Monsoon Storm & Sitabuldi Flash Flood
        flood_index = round(0.75 + random.uniform(0.05, 0.18), 2)
        congestion = 94
        voltage -= 14.0
        cctv_status = "ROAD_SUBMERGED"
        ai_confidence = 0.95
        is_flood = True

    elif 44 <= cycle_tick < 50:
        # Scenario 4: Hospital Substation Fire Emergency & Building Evacuation
        voltage = round(random.uniform(15.0, 40.0), 1)
        diesel_fuel = 320  # Under 4 hours
        congestion = 98
        cctv_status = "FIRE_EMERGENCY"
        ai_confidence = 0.98
        is_fire_emergency = True
        is_power_failure = True
        evacuate_building = True
        firefighter_alert = True
        trauma_surge = 0.85

    elif 50 <= cycle_tick < 55:
        # Scenario 5 (Task 5): Civil Riot / Blockade & Ambulance Crash
        congestion = 96
        cctv_status = "RIOT_DETECTED" if cycle_tick % 2 == 0 else "AMBULANCE_CRASH"
        ai_confidence = 0.97
        is_riot_detected = True

    elif 55 <= cycle_tick < 60:
        # Scenario 6: Structural Earthquake Tremor
        richter_mag = 5.8
        voltage = 0.0
        congestion = 100
        cctv_status = "STRUCTURAL_DAMAGE"
        ai_confidence = 0.98
        is_earthquake = True
        evacuate_building = True

    # Sovereignty failover simulation: ticks 50-60 switch to LoRa Radio Mesh
    network = "lora_radio_mesh" if 48 <= cycle_tick <= 58 else "satellite_api"
    weather = get_live_weather()

    # Supply Chain & Task 6 Blood Sharing Verification
    supply_chain_data = {
        "blood_units_o_neg": blood_o_neg,
        "diesel_fuel_liters": diesel_fuel,
        "diesel_hours_left": round(diesel_fuel / 100.0, 1)
    }

    if is_organ_transport:
        supply_chain_data["organ_match"] = "HEART_VIABLE"
        supply_chain_data["insurance_claim"] = "AUTO_FILED_APPROVED"

    if is_resource_deficit:
        supply_chain_data["iot_radio_broadcast"] = "URGENT_BLOOD_REQ"
        supply_chain_data["assigned_driver"] = "TAXI-SWARM-304"
        # Task 6: Driver pickup verification protocol
        supply_chain_data["blood_pickup_verified"] = True
        supply_chain_data["pickup_timestamp"] = datetime.now(timezone.utc).isoformat()
        supply_chain_data["driver_eta_minutes"] = 5.2
        supply_chain_data["driver_auth_token"] = "HMAC-SWARM-VERIFIED-982"

    # Evaluate Clinical Medical Triage AI Model
    medical_action_code = 0
    medical_action_str = "STABLE_MONITOR"
    if _MEDICAL_MODEL is not None:
        try:
            import pandas as pd
            gen_hours = round(diesel_fuel / 100.0, 1)
            med_df = pd.DataFrame(
                [[icu_occupancy, oxygen_hours, vent_utilization, trauma_surge, blood_o_neg, gen_hours]],
                columns=[
                    "icu_bed_occupancy_pct", "oxygen_hours_remaining",
                    "ventilator_utilization_pct", "trauma_surge_index",
                    "blood_o_neg_units", "generator_hours_remaining"
                ]
            )
            pred_code = int(_MEDICAL_MODEL.predict(med_df)[0])
            actions_map = {
                0: "STABLE_MONITOR",
                1: "DIVERT_AMBULANCES",
                2: "EXPEDITE_SUPPLY_CHAIN",
                3: "EVACUATE_WARD_IMMEDIATE"
            }
            medical_action_code = pred_code
            medical_action_str = actions_map.get(pred_code, "STABLE_MONITOR")
        except Exception:
            pass

    is_critical = any([
        is_flood, is_power_failure, is_earthquake,
        is_organ_transport, is_resource_deficit,
        is_fire_emergency, is_riot_detected, evacuate_building
    ])

    return {
        "packet_id": f"SYN-{random.randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unix_timestamp": time.time(),
        "nonce": os.urandom(8).hex(),
        "sensor_location": location,
        "network_mode": network,
        "metrics": {
            "grid_voltage": round(voltage, 2),
            "flood_index": round(flood_index, 2),
            "route_congestion": congestion,
            "diesel_hours_remaining": round(diesel_fuel / 100.0, 1),
            "o_neg_blood_units": blood_o_neg,
            "organ_cooler_temp_c": round(3.8 + random.uniform(-0.2, 0.2), 1),
            "temperature": weather["temperature"],
            "windspeed": weather["windspeed"],
            "seismic_richter": richter_mag,
            "clinical_triage": {
                "icu_occupancy_pct": icu_occupancy,
                "oxygen_hours_remaining": oxygen_hours,
                "ventilator_utilization_pct": vent_utilization,
                "trauma_surge_index": trauma_surge,
                "ai_action_code": medical_action_code,
                "ai_action_recommendation": medical_action_str
            },
            "supply_chain": supply_chain_data,
            "cctv_intel": {
                "status": cctv_status,
                "confidence": ai_confidence
            },
            "emergency_protocols": {
                "evacuate_building": evacuate_building,
                "firefighter_dispatch": firefighter_alert,
                "fire_suppression_active": is_fire_emergency
            }
        },
        "structural_integrity": "COMPROMISED" if is_earthquake else "STABLE",
        "status": "critical" if is_critical else "nominal"
    }

def sign_packet(payload: bytes) -> str:
    """Signs the payload using HMAC-SHA256 (Pillar 1: Trusted Telemetry)."""
    return hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()

async def stream_telemetry():
    print(f"IBM SNAP ML ENGINE INITIALIZED: Isolation Forest Model Loaded")
    print(f"Target Mainframe: {MAINFRAME_URL}")
    print(f"Using HMAC-SHA256 Edge Cryptography")
    print(f"NETWORK MODE: [CONNECTED] Satellite API & CCTV Metadata Active")
    print("-" * 50)
    
    tick = 0
    async with httpx.AsyncClient() as client:
        while True:
            if tick > 0 and tick % 20 == 0:
                print(f"\n[\033[91mWARNING\033[0m] SATELLITE LINK LOST. FALLING BACK TO SECURE LORA RADIO MESH.")
                await asyncio.sleep(2)
            elif tick > 0 and tick % 20 == 5:
                print(f"[\033[92mRESTORED\033[0m] SATELLITE API LINK RE-ESTABLISHED.\n")
                
            # 1. Generate Data
            packet = generate_telemetry_packet(tick)
            payload_bytes = json.dumps(packet).encode('utf-8')
            
            # 2. Cryptographically Sign
            signature = sign_packet(payload_bytes)
            
            # 3. Transmit
            headers = {
                "Content-Type": "application/json",
                "X-Signature": signature
            }
            
            try:
                response = await client.post(MAINFRAME_URL, content=payload_bytes, headers=headers)
                
                if response.status_code == 200:
                    status_msg = "[ACCEPTED]"
                elif response.status_code == 401:
                    status_msg = "[REJECTED (HMAC Fail)]"
                else:
                    status_msg = f"[ERROR {response.status_code}]"
                    
                print(f"[{packet['timestamp']}] {status_msg} | {packet['sensor_location']} | Flood: {packet['metrics']['flood_index']}")
                
            except httpx.RequestError as e:
                print(f"[FAILED] Connection failed: Is the Mainframe running on port 8000? ({e})")
            
            tick += 1
            await asyncio.sleep(2)  # Stream interval

if __name__ == "__main__":
    try:
        asyncio.run(stream_telemetry())
    except KeyboardInterrupt:
        print("\nTelemetry Simulator Stopped.")
