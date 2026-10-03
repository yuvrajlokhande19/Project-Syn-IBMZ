import logging
import asyncio
import os
import httpx
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Fetch credentials from environment variables (with fallbacks to Synth City config)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8691301021:AAE0hJe2nU_LqUDnj-HK6NMd037QIYwJtmc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8889864487")

def format_alert_message(data: Dict[str, Any]) -> str:
    """Formats telemetry data into a Telegram-friendly alert message in English, Hindi, and Marathi."""
    packet_id = data.get("packet_id", "UNKNOWN-ID")
    location = data.get("sensor_location", "Unknown Location")
    
    # In a real s390x environment, a local Big-Endian LLM (like Phi-3) would dynamically translate this.
    # For this task, we format the deterministic output in 3 languages.
    
    msg_en = f"🚨 *MAINFRAME ALERT* 🚨\n"
    msg_en += f"Packet: `{packet_id}`\n"
    msg_en += f"Location: `{location}`\n"
    msg_en += "Status: Anomaly Detected! Rerouting ambulances.\n"
    
    msg_hi = f"\n🔴 *मुख्य सर्वर चेतावनी* 🔴\n"
    msg_hi += f"पैकेट: `{packet_id}`\n"
    msg_hi += f"स्थान: `{location}`\n"
    msg_hi += "स्थिति: विसंगति पाई गई! एंबुलेंस का मार्ग बदला जा रहा है।\n"
    
    msg_mr = f"\n⚠️ *मुख्य सर्व्हर इशारा* ⚠️\n"
    msg_mr += f"पॅकेट: `{packet_id}`\n"
    msg_mr += f"ठिकाण: `{location}`\n"
    msg_mr += "स्थिती: विसंगती आढळली! रुग्णवाहिकेचा मार्ग बदलत आहे.\n"
    
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
    # Assuming Pair 2 Logic Engine has flagged an anomaly in the data
    metrics = data.get("metrics", {})
    flood_index = metrics.get("flood_index", 0.0)
    
    # Anomaly condition triggering translation and dispatch
    if flood_index > 0.8:
        message = format_alert_message(data)
        await send_telegram_alert(message)
