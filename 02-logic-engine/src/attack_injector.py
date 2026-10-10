"""
================================================================================
Project Syn / AegisCore: Cyber Attack Injector & Security Verification Suite
Target: IBM LinuxONE s390x CPACF Zero-Trust Gateway
================================================================================
This tool executes automated and targeted adversarial attack vectors against
the Mainframe Ingestion Gate to prove zero-trust defenses:
1. Tampered HMAC: Payload altered post-signature -> 401 Unauthorized
2. Replayed Nonce: Exact same nonce fired twice -> 401 Unauthorized
3. Stale Timestamp: Packet generated with old timestamp (>30s) -> 401 Unauthorized
4. Spoofed Physics: Sensor injection violating physical reality -> 403 Forbidden
5. Baseline Valid: Legitimately signed packet with fresh nonce -> 200 OK
================================================================================
"""

import os
import sys
import time
import json
import hmac
import hashlib
import random
import argparse
import requests
from typing import Dict, Any, Tuple


from dotenv import load_dotenv

# Load environment configuration (.env from local and project root)
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

SECRET_KEY = os.getenv("MAINFRAME_SECRET_KEY", "mainframe_secret_key").encode("utf-8")
DEFAULT_TARGET_URL = os.getenv("MAINFRAME_INGEST_URL", "http://127.0.0.1:8000/api/telemetry/ingest")


def sign_payload(payload_bytes: bytes, secret: bytes = SECRET_KEY) -> str:
    """Computes HMAC-SHA256 signature simulating CPACF hardware cryptography."""
    return hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()


def create_base_packet() -> Dict[str, Any]:
    """Generates a nominal baseline packet."""
    now = time.time()
    return {
        "packet_id": f"SYN-TEST-{random.randint(10000, 99999)}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "unix_timestamp": now,
        "nonce": os.urandom(8).hex(),
        "sensor_location": "GMC_Nagpur",
        "network_mode": "satellite_api",
        "metrics": {
            "grid_voltage": 220.5,
            "flood_index": 0.05,
            "route_congestion": 35,
            "temperature": 34.0,
            "windspeed": 14.5,
            "supply_chain": {
                "blood_units_o_neg": 50,
                "diesel_fuel_liters": 2500
            },
            "cctv_intel": {
                "status": "CLEAR",
                "confidence": 0.99
            }
        },
        "status": "nominal"
    }


def send_packet(url: str, payload_bytes: bytes, signature: str) -> Tuple[int, str]:
    """Transmits packet with headers to mainframe ingest endpoint."""
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature
    }
    try:
        resp = requests.post(url, data=payload_bytes, headers=headers, timeout=5.0)
        return resp.status_code, resp.text
    except requests.exceptions.RequestException as e:
        return 0, f"Connection Failed: {e}"


def test_baseline_valid(url: str) -> bool:
    print("\n" + "="*60)
    print("TEST 1: BASELINE NOMINAL PACKET (Valid HMAC, Fresh Nonce, Current TS)")
    print("="*60)
    packet = create_base_packet()
    body = json.dumps(packet).encode("utf-8")
    sig = sign_payload(body)

    status_code, text = send_packet(url, body, sig)
    print(f"[*] Sent Packet ID: {packet['packet_id']} with Nonce: {packet['nonce']}")
    print(f"[*] Response Code: {status_code}")
    print(f"[*] Response Body: {text}")

    if status_code == 200:
        print("[PASS] Nominal packet accepted into queue!")
        return True
    else:
        print(f"[FAIL] Expected 200 OK, got {status_code}")
        return False


def test_tampered_hmac(url: str) -> bool:
    print("\n" + "="*60)
    print("TEST 2: TAMPER ATTACK (Payload byte modified after HMAC generation)")
    print("="*60)
    packet = create_base_packet()
    body = json.dumps(packet).encode("utf-8")
    sig = sign_payload(body)

    # Attacker alters grid_voltage in payload without knowing secret key
    packet["metrics"]["grid_voltage"] = 110.0
    tampered_body = json.dumps(packet).encode("utf-8")

    status_code, text = send_packet(url, tampered_body, sig)
    print(f"[*] Sent tampered payload with original signature: {sig[:16]}...")
    print(f"[*] Response Code: {status_code}")
    print(f"[*] Response Body: {text}")

    if status_code == 401:
        print("[PASS] CPACF Gate successfully detected HMAC mismatch and rejected packet (401)!")
        return True
    else:
        print(f"[FAIL] Expected 401 Unauthorized, got {status_code}")
        return False


def test_replayed_nonce(url: str) -> bool:
    print("\n" + "="*60)
    print("TEST 3: REPLAY ATTACK (Firing identical nonce twice)")
    print("="*60)
    packet = create_base_packet()
    body = json.dumps(packet).encode("utf-8")
    sig = sign_payload(body)

    # First transmission: should succeed
    status_code1, _ = send_packet(url, body, sig)
    print(f"[*] Round 1 (Legitimate): Code {status_code1}")

    # Second transmission: replay exact same packet and nonce
    status_code2, text2 = send_packet(url, body, sig)
    print(f"[*] Round 2 (Replay Injection): Code {status_code2}")
    print(f"[*] Response Body: {text2}")

    if status_code2 == 401 and "Replay" in text2:
        print("[PASS] Monotonic Nonce Cache intercepted duplicate nonce and blocked replay (401)!")
        return True
    elif status_code2 == 401:
        print("[PASS] Replay packet rejected with 401!")
        return True
    else:
        print(f"[FAIL] Expected 401 Unauthorized on replay, got {status_code2}")
        return False


def test_stale_timestamp(url: str) -> bool:
    print("\n" + "="*60)
    print("TEST 4: STALE TELEMETRY ATTACK (Timestamp 90 seconds in past)")
    print("="*60)
    packet = create_base_packet()
    stale_ts = time.time() - 90.0  # 90s older than current time
    packet["unix_timestamp"] = stale_ts
    packet["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stale_ts))

    body = json.dumps(packet).encode("utf-8")
    sig = sign_payload(body)

    status_code, text = send_packet(url, body, sig)
    print(f"[*] Sent packet with drift: -90.0s")
    print(f"[*] Response Code: {status_code}")
    print(f"[*] Response Body: {text}")

    if status_code == 401 and "Stale" in text:
        print("[PASS] Timestamp drift validator rejected stale packet (401)!")
        return True
    elif status_code == 401:
        print("[PASS] Stale packet rejected with 401!")
        return True
    else:
        print(f"[FAIL] Expected 401 Unauthorized on stale packet, got {status_code}")
        return False


def test_spoofed_physics(url: str) -> bool:
    print("\n" + "="*60)
    print("TEST 5: SPOOFED PHYSICS ATTACK (Severe flood with zero congestion & high voltage)")
    print("="*60)
    packet = create_base_packet()
    # Impossible physics: severe flood (0.95), full voltage (230V), empty streets (5% traffic)
    packet["metrics"]["flood_index"] = 0.95
    packet["metrics"]["grid_voltage"] = 230.0
    packet["metrics"]["route_congestion"] = 5

    body = json.dumps(packet).encode("utf-8")
    sig = sign_payload(body)

    status_code, text = send_packet(url, body, sig)
    print(f"[*] Sent physically contradictory telemetry: Flood=0.95, Volt=230V, Congest=5%")
    print(f"[*] Response Code: {status_code}")
    print(f"[*] Response Body: {text}")

    if status_code == 403:
        print("[PASS] Cross-Sensor Sanity Model rejected spoofed physics packet (403 Forbidden)!")
        return True
    else:
        print(f"[FAIL] Expected 403 Forbidden on spoofed physics, got {status_code}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Project Syn Adversarial Attack Injector")
    parser.add_argument("--target", default=DEFAULT_TARGET_URL, help="Mainframe ingest API URL")
    parser.add_argument("--attack", choices=["all", "baseline", "tamper", "replay", "stale", "spoof"],
                        default="all", help="Attack vector to execute")
    args = parser.parse_args()

    print(f"Target Gateway: {args.target}")
    results = {}

    if args.attack in ("all", "baseline"):
        results["baseline"] = test_baseline_valid(args.target)
    if args.attack in ("all", "tamper"):
        results["tamper"] = test_tampered_hmac(args.target)
    if args.attack in ("all", "replay"):
        results["replay"] = test_replayed_nonce(args.target)
    if args.attack in ("all", "stale"):
        results["stale"] = test_stale_timestamp(args.target)
    if args.attack in ("all", "spoof"):
        results["spoof"] = test_spoofed_physics(args.target)

    print("\n" + "="*60)
    print("ATTACK INJECTION SUITE RESULTS SUMMARY")
    print("="*60)
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f" - {test_name.upper().ljust(15)}: {status}")
        if not passed:
            all_passed = False

    print("="*60)
    if all_passed:
        print("[SUCCESS] All CPACF zero-trust gates verified functional.")
        sys.exit(0)
    else:
        print("[ALERT] One or more security tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
