import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

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
    
    if anomaly_type == "FLOOD":
        status_en = f"Critical flooding detected! Rerouting ambulances via: {safe_route}"
        status_hi = f"गंभीर बाढ़! एंबुलेंस का नया मार्ग: {safe_route}"
        status_mr = f"गंभीर पूर! रुग्णवाहिकेचा नवीन मार्ग: {safe_route}"
    elif anomaly_type == "POWER_FAILURE":
        status_en = f"Power Grid Failure! ICU transitioning to backup generators."
        status_hi = f"पावर ग्रिड फेल! आईसीयू बैकअप जनरेटर पर जा रहा है।"
        status_mr = f"वीज पुरवठा खंडित! आयसीयू जनरेटरवर हलवत आहे."
    elif anomaly_type == "EARTHQUAKE":
        status_en = f"STRUCTURAL DAMAGE (EARTHQUAKE)! Immediate Fleet Reroute."
        status_hi = f"भूकंप से क्षति! तुरंत फ्लीट को डायवर्ट करें।"
        status_mr = f"भूकंपामुळे नुकसान! रुग्णवाहिकांना तत्काळ दुसरा मार्ग द्या."
    elif anomaly_type == "ORGAN_TRANSPLANT":
        status_en = f"HEART MATCH FOUND. GREEN CORRIDOR INITIATED. Auto-Insurance Claim Filed."
        status_hi = f"हृदय मैच मिला। ग्रीन कॉरिडोर लागू। बीमा दावा स्वतः दर्ज।"
        status_mr = f"हृदय जुळले. ग्रीन कॉरिडॉर सुरू. विमा दावा आपोआप दाखल."
    else:
        status_en = "General Anomaly."
        status_hi = "सामान्य विसंगति।"
        status_mr = "सामान्य विसंगती."

    msg_en = f"🚨 *PROJECT SYN MAINFRAME ALERT* 🚨\n"
    msg_en += f"Network: `{net_flag}`\n"
    msg_en += f"Location: `{location}`{weather_info}{intel_string}\n"
    msg_en += f"Status: {status_en}\n"
    
    msg_hi = f"\n🔴 *मुख्य सर्वर चेतावनी* 🔴\n"
    msg_hi += f"स्थान: `{location}`{weather_info}{intel_string}\n"
    msg_hi += f"स्थिति: {status_hi}\n"
    
    msg_mr = f"\n⚠️ *मुख्य सर्व्हर इशारा* ⚠️\n"
    msg_mr += f"ठिकाण: `{location}`{weather_info}{intel_string}\n"
    msg_mr += f"स्थिती: {status_mr}\n"
    
    return msg_en + msg_hi + msg_mr

def dispatch_alert(raw_message: str):
    logger.info(f"Telegram alert dispatched: \n{raw_message}")
