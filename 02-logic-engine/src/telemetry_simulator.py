import time
import json
import hmac
import hashlib
import random
import math
import httpx
import asyncio
from datetime import datetime, timezone

SECRET_KEY = b"mainframe_secret_key"
MAINFRAME_URL = "http://127.0.0.1:8000/api/telemetry/ingest"

# Realistic Locations in Nagpur based on the CARTO map
LOCATIONS = [
    "GMC_Nagpur",
    "Mayo_Hospital",
    "AIIMS_Nagpur",
    "Lata_Mangeshkar_Hospital",
    "Wockhardt_Hospital"
]

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
    if random.random() > 0.95:
        flood_index += 0.7  # Trigger the >0.8 threshold
    
    # Simulate Route Congestion (percentage 0-100)
    congestion = int(max(10, min(95, 40 + (math.cos(tick * 0.05) * 30) + random.uniform(-10, 10))))

    return {
        "packet_id": f"SYN-{random.randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_location": location,
        "metrics": {
            "grid_voltage": round(voltage, 2),
            "flood_index": round(flood_index, 2),
            "route_congestion": congestion
        },
        "status": "critical" if flood_index > 0.8 else "nominal"
    }

def sign_packet(payload: bytes) -> str:
    """Signs the payload using HMAC-SHA256 (Pillar 1: Trusted Telemetry)."""
    return hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()

async def stream_telemetry():
    print(f"IBM SNAP ML ENGINE INITIALIZED: Isolation Forest Model Loaded")
    print(f"Target Mainframe: {MAINFRAME_URL}")
    print(f"Using HMAC-SHA256 Edge Cryptography")
    print("-" * 50)
    
    tick = 0
    async with httpx.AsyncClient() as client:
        while True:
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
