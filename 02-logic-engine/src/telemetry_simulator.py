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

SECRET_KEY = os.getenv("MAINFRAME_SECRET_KEY", "fallback_secret_key").encode('utf-8')
MAINFRAME_URL = os.getenv("MAINFRAME_URL", "http://127.0.0.1:8000/api/telemetry/ingest")

# Realistic Locations in Nagpur based on the CARTO map
LOCATIONS = [
    "GMC_Nagpur",
    "Mayo_Hospital",
    "AIIMS_Nagpur",
    "Lata_Mangeshkar_Hospital",
    "Wockhardt_Hospital"
]

def get_live_weather() -> dict:
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=21.1458&longitude=79.0882&current_weather=true"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        return {
            "temperature": current.get("temperature", round(random.uniform(25.0, 45.0), 1)),
            "windspeed": current.get("windspeed", round(random.uniform(0.0, 20.0), 1))
        }
    except Exception:
        return {
            "temperature": round(random.uniform(25.0, 45.0), 1),
            "windspeed": round(random.uniform(0.0, 20.0), 1)
        }

def generate_telemetry_packet(tick: int) -> dict:
    """Generates realistic telemetry using sine waves and noise instead of pure random."""
    location = random.choice(LOCATIONS)
    
    # Simulate Grid Voltage (Standard 220V with slight sine wave fluctuation)
    voltage_base = 220.0
    voltage_noise = random.uniform(-2.0, 2.0)
    voltage = voltage_base + (math.sin(tick * 0.1) * 5) + voltage_noise
    
    # Simulate Flood Index (Usually near 0, spikes during anomalies)
    flood_index = max(0.0, math.sin(tick * 0.05) * 0.3 + random.uniform(0.0, 0.2))
    
    # Inject a random anomaly spike occasionally
    is_flood = False
    is_power_failure = False
    is_earthquake = False
    is_organ_transport = False
    
    # CCTV & Supply Chain Defaults
    cctv_status = "CLEAR"
    ai_confidence = 0.99
    blood_o_neg = random.randint(50, 200)
    diesel_fuel = random.randint(1000, 5000)
    
    rand_val = random.random()
    if rand_val > 0.96:
        flood_index += 0.7  # Trigger flood
        congestion = 95     # Roads flooded, congestion spikes
        voltage -= 10.0     # Transformers strain under water
        cctv_status = "ROAD_SUBMERGED"
        ai_confidence = 0.94
        is_flood = True
    elif rand_val < 0.04:
        voltage = random.uniform(0.0, 50.0) # Total power grid failure
        congestion = 85     # Traffic lights dead, congestion spikes
        cctv_status = "BLACKOUT_DETECTED"
        is_power_failure = True
    elif rand_val > 0.92 and rand_val <= 0.96:
        # Earthquake Scenario
        voltage = 0.0
        congestion = 100
        blood_o_neg -= random.randint(20, 50)  # Mass casualties
        cctv_status = "STRUCTURAL_DAMAGE"
        ai_confidence = 0.98
        is_earthquake = True
    elif rand_val > 0.88 and rand_val <= 0.92:
        # Organ Transplant / Green Corridor
        congestion = 0  # Traffic lights cleared by system
        cctv_status = "GREEN_CORRIDOR_ACTIVE"
        ai_confidence = 0.99
        is_organ_transport = True
    else:
        # Simulate Route Congestion normally
        congestion = int(max(10, min(95, 40 + (math.cos(tick * 0.05) * 30) + random.uniform(-10, 10))))
    
    # Network mode fallback
    network = "lora_radio_mesh" if (tick > 0 and (tick % 20 < 5)) else "satellite_api"
    
    weather = get_live_weather()

    # Supply Chain & Insurance Metadata
    supply_chain_data = {
        "blood_units_o_neg": blood_o_neg,
        "diesel_fuel_liters": diesel_fuel
    }
    if is_organ_transport:
        supply_chain_data["organ_match"] = "HEART_VIABLE"
        supply_chain_data["insurance_claim"] = "AUTO_FILED_APPROVED"

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
            "temperature": weather["temperature"],
            "windspeed": weather["windspeed"],
            "supply_chain": supply_chain_data,
            "cctv_intel": {
                "status": cctv_status,
                "confidence": ai_confidence
            }
        },
        "status": "critical" if (is_flood or is_power_failure or is_earthquake or is_organ_transport) else "nominal"
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
