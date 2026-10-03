import logging
import requests
import json
import os
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImMzYzc5ZGUzNjEyNjRiMzA5ODM3NjQ5NzVlYjQzZTY1IiwiaCI6Im11cm11cjY0In0=")

def generate_local_s390x_llm(anomaly_type: str, location: str, safe_route: str) -> str:
    """
    Simulates the Big-Endian Phi-3 LLM running natively on the s390x architecture.
    This is triggered ONLY when internet is down (LoRaWAN / Sovereign Mode).
    """
    logger.info("INTERNET DOWN. FALLING BACK TO LOCAL BIG-ENDIAN PHI-3 LLM (s390x)...")
    time.sleep(1.5) # Simulate local inference latency
    
    if anomaly_type == "FLOOD":
        return (
            "[EN] Flood detected at {loc}. Evacuate via {route}.\n"
            "[HI] {loc} में बाढ़ का पता चला। {route} के माध्यम से खाली करें।\n"
            "[MR] {loc} मध्ये पूर आला आहे. {route} मार्गे बाहेर पडा."
        ).format(loc=location, route=safe_route)
    elif anomaly_type == "RESOURCE_DEFICIT":
        return (
            "[EN] Critical blood shortage at {loc}. Requesting civilian transport.\n"
            "[HI] {loc} में रक्त की भारी कमी है। नागरिक परिवहन का अनुरोध किया गया है।\n"
            "[MR] {loc} मध्ये रक्ताची तीव्र कमतरता आहे. नागरी वाहतुकीची विनंती करत आहे."
        ).format(loc=location)
    elif anomaly_type == "EARTHQUAKE":
        return (
            "[EN] Structural damage at {loc}. Rerouting fleet.\n"
            "[HI] {loc} में संरचनात्मक क्षति। बेड़े का मार्ग बदल रहा है।\n"
            "[MR] {loc} मध्ये संरचनात्मक नुकसान. ताफ्याचा मार्ग बदलत आहे."
        ).format(loc=location)
    else:
        return (
            "[EN] Emergency at {loc}. Proceed with caution.\n"
            "[HI] {loc} में आपातकाल। सावधानी से आगे बढ़ें।\n"
            "[MR] {loc} मध्ये आणीबाणी. सावधगिरीने पुढे जा."
        ).format(loc=location)

def generate_llm_dispatch(prompt: str) -> str:
    """Uses OpenRouter AI to generate a real dynamic dispatch message."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=5
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenRouter Error: {e}")
    return ""

def format_alert_message(data: Dict[str, Any], anomaly_type: str, safe_route: str = "") -> str:
    """Formats telemetry data into a Telegram-friendly alert message in English, Hindi, and Marathi."""
    packet_id = data.get("packet_id", "UNKNOWN-ID")
    location = data.get("sensor_location", "Unknown Location")
    network = data.get("network_mode", "satellite_api").upper()
    
    metrics = data.get("metrics", {})
    weather_temp = metrics.get("weather_temperature")
    weather_info = f" | Temp: {weather_temp}°C" if weather_temp else ""
    
    cctv = metrics.get("cctv_intel", {}).get("status", "UNKNOWN")
    blood = metrics.get("supply_chain", {}).get("blood_units_o_neg", "N/A")
    
    net_flag = "📡 SATELLITE API" if network != "LORA_RADIO_MESH" else "📻 LORA RADIO MESH (SOVEREIGN MODE)"
    intel_string = f"\nEdge AI CCTV: {cctv} | O-Negative Blood: {blood} units"
    
    # -------------------------------------------------------------
    # PILLAR 2: SOVEREIGNTY FALLOVER (Cloud AI -> Local s390x AI)
    # -------------------------------------------------------------
    if network == "LORA_RADIO_MESH":
        # Internet is down! Run local Big-Endian AI
        llm_text = generate_local_s390x_llm(anomaly_type, location, safe_route) if anomaly_type != "NOMINAL" else ""
    else:
        # Internet is up! Run Cloud AI
        llm_prompt = f"Write a VERY short (3 sentences max) emergency dispatch alert for {anomaly_type} at {location}. Include: {safe_route}. Write it in English, Hindi, and Marathi."
        llm_text = generate_llm_dispatch(llm_prompt) if anomaly_type != "NOMINAL" else ""
    
    if anomaly_type == "FLOOD":
        status_en = f"Critical flooding detected! Rerouting ambulances via: {safe_route}"
    elif anomaly_type == "POWER_FAILURE":
        status_en = f"Power Grid Failure! ICU transitioning to backup generators."
    elif anomaly_type == "EARTHQUAKE":
        status_en = f"STRUCTURAL DAMAGE (EARTHQUAKE)! Immediate Fleet Reroute."
    elif anomaly_type == "ORGAN_TRANSPLANT":
        status_en = f"HEART MATCH FOUND. GREEN CORRIDOR INITIATED. Auto-Insurance Claim Filed."
    elif anomaly_type == "RESOURCE_DEFICIT":
        status_en = f"CRITICAL BLOOD SHORTAGE. IoT Radio Broadcast Sent. Civilian Swarm Driver assigned."
    else:
        status_en = "General Anomaly."

    msg = f"🚨 *PROJECT SYN MAINFRAME ALERT* 🚨\n"
    msg += f"Network: `{net_flag}`\n"
    msg += f"Location: `{location}`{weather_info}{intel_string}\n"
    msg += f"System Status: {status_en}\n"
    
    if llm_text:
        source = "🧠 [LOCAL S390X PHI-3 INFERENCE]" if network == "LORA_RADIO_MESH" else "☁️ [CLOUD OPENROUTER AI]"
        msg += f"\n---\n{source}:\n{llm_text}\n"
    
    return msg

def dispatch_alert(raw_message: str):
    logger.info(f"Telegram alert dispatched: \n{raw_message}")
