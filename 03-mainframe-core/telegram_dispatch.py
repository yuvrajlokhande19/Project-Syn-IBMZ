import logging
import asyncio
import os
import httpx
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fetch credentials strictly from environment variables (.env)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def format_alert_message(data: Dict[str, Any], anomaly_type: str, safe_route: str = "") -> str:
    """Formats telemetry data into a Telegram-friendly alert message in English, Hindi, and Marathi."""
    packet_id = data.get("packet_id", "UNKNOWN-ID")
    location = data.get("sensor_location", "Unknown Location")
    network = data.get("network_mode", "satellite_api").upper()
    
    net_flag = "📡 SATELLITE API" if network != "LORA_RADIO_MESH" else "📻 LORA RADIO MESH (SOVEREIGN MODE)"
    
    if anomaly_type == "FLOOD":
        status_en = f"Critical flooding detected! Rerouting ambulances via: {safe_route}"
        status_hi = f"गंभीर बाढ़! एंबुलेंस का नया मार्ग: {safe_route}"
        status_mr = f"गंभीर पूर! रुग्णवाहिकेचा नवीन मार्ग: {safe_route}"
    elif anomaly_type == "POWER":
        status_en = f"Power Grid Failure! ICU transitioning to backup generators."
        status_hi = f"पावर ग्रिड फेल! आईसीयू बैकअप जनरेटर पर जा रहा है।"
        status_mr = f"वीज पुरवठा खंडित! आयसीयू जनरेटरवर हलवत आहे."
    else:
        status_en = "General Anomaly."
        status_hi = "सामान्य विसंगति।"
        status_mr = "सामान्य विसंगती."

    msg_en = f"🚨 *MAINFRAME ALERT* 🚨\n"
    msg_en += f"Network: `{net_flag}`\n"
    msg_en += f"Location: `{location}`\n"
    msg_en += f"Status: {status_en}\n"
    
    msg_hi = f"\n🔴 *मुख्य सर्वर चेतावनी* 🔴\n"
    msg_hi += f"स्थान: `{location}`\n"
    msg_hi += f"स्थिति: {status_hi}\n"
    
    msg_mr = f"\n⚠️ *मुख्य सर्व्हर इशारा* ⚠️\n"
    msg_mr += f"ठिकाण: `{location}`\n"
    msg_mr += f"स्थिती: {status_mr}\n"
    
    return msg_en + msg_hi + msg_mr

async def send_telegram_alert(message: str) -> bool:
    """Sends a message via Telegram Bot API using httpx."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials missing. Skipping alert dispatch.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram alert sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

async def process_and_alert(data: Dict[str, Any]):
    """Analyzes telemetry data and triggers alerts if anomaly thresholds are crossed."""
    metrics = data.get("metrics", {})
    flood_index = metrics.get("flood_index", 0.0)
    voltage = metrics.get("grid_voltage", 220.0)
    location = data.get("sensor_location", "UNKNOWN")
    
    anomaly_type = None
    if flood_index > 0.8:
        anomaly_type = "FLOOD"
    elif voltage < 150.0:
        anomaly_type = "POWER"
        
    if anomaly_type:
        from hash_ledger import HashLedger
        ledger = HashLedger()
        
        # Determine Safe Route if Flooded
        safe_route = ""
        if anomaly_type == "FLOOD":
            try:
                from routing_algorithm import NagpurHospitalRouter
                router = NagpurHospitalRouter()
                router.update_weights(location, penalty=999)
                target_hospital = "Mayo_Hospital" if location != "Mayo_Hospital" else "GMC_Nagpur"
                path, cost = router.dijkstra("AIIMS_Nagpur", target_hospital)
                safe_route = " -> ".join(path)
            except Exception as e:
                logger.error(f"Routing error: {e}")
                safe_route = "Standard Backup Route"
                
        # Generate the LLM message
        message = format_alert_message(data, anomaly_type, safe_route)
        
        # Save to DB so frontend can fetch it
        ledger.record_alert(location, message)
        
        # Dispatch to actual Telegram
        await send_telegram_alert(message)
