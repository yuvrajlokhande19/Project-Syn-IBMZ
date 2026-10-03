import logging
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Stub configuration
TELEGRAM_BOT_TOKEN = "stub_bot_token"
TELEGRAM_CHAT_ID = "stub_chat_id"

def format_alert_message(data: Dict[str, Any]) -> str:
    """Formats telemetry data into a Telegram-friendly alert message."""
    device_id = data.get("device_id", "Unknown Device")
    status = data.get("status", "Unknown Status")
    
    msg = f"🚨 *Mainframe Core Alert* 🚨\n\n"
    msg += f"Device: `{device_id}`\n"
    msg += f"Status: `{status}`\n"
    
    if "metrics" in data:
        msg += "\n*Metrics:*\n"
        for k, v in data.get("metrics", {}).items():
            msg += f"• {k}: {v}\n"
            
    return msg

async def send_telegram_alert(message: str) -> bool:
    """Stub function to send a message via Telegram Bot API."""
    # In a real implementation, this would use aiohttp or httpx to POST to 
    # https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage
    logger.info(f"Simulating Telegram alert dispatch to chat {TELEGRAM_CHAT_ID}")
    logger.debug(f"Message content:\n{message}")
    
    # Simulate network delay
    await asyncio.sleep(0.1)
    
    return True

async def process_and_alert(data: Dict[str, Any]):
    """Analyzes telemetry data and triggers alerts if necessary."""
    # Example condition: send alert if status is 'error' or 'critical'
    status = data.get("status", "").lower()
    
    if status in ("error", "critical"):
        message = format_alert_message(data)
        await send_telegram_alert(message)
