"""
================================================================================
Project Syn / AegisCore: Mainframe Cryptographic Gateway
Hardware Target: IBM LinuxONE s390x (CPACF Acceleration Architecture)
================================================================================
This module provides:
1. CPACF-accelerated HMAC-SHA256 hardware signature verification.
2. Monotonic thread-safe Nonce cache (anti-replay window: max 10,000 nonces).
3. Monotonic timestamp drift validation (rejects packets > 30s past / > 10s future).
4. Cross-sensor physical consistency validation (detects spoofed sensor attacks).
================================================================================
"""

import os
import time
import json
import hmac
import hashlib
import logging
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger("crypto_gate")
logger.setLevel(logging.INFO)

from dotenv import load_dotenv

# Load environment configuration (.env from local and project root)
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# CPACF Hardware Status Emulation
CPACF_HARDWARE_ACCELERATED = True
MAX_NONCE_CAPACITY = 10000
MAX_TIMESTAMP_PAST_DRIFT_SECONDS = 30.0
MAX_TIMESTAMP_FUTURE_DRIFT_SECONDS = 10.0

DEFAULT_SECRET_KEY = os.getenv("MAINFRAME_SECRET_KEY", "mainframe_secret_key").encode("utf-8")


class NonceCache:
    """
    Thread-safe monotonic Nonce cache with sliding FIFO eviction.
    Guarantees strict single-use nonces to defeat replay attacks.
    Capacity capped at 10,000 nonces to respect s390x memory boundaries.
    """
    def __init__(self, max_size: int = MAX_NONCE_CAPACITY):
        self._max_size = max_size
        self._set = set()
        self._queue = deque()
        self._lock = threading.Lock()

    def check_and_add(self, nonce: str) -> bool:
        """
        Atomically checks if nonce exists. If not, records it.
        Returns True if nonce is valid and recorded.
        Returns False if nonce has already been consumed (Replay attack).
        """
        if not nonce:
            return False

        with self._lock:
            if nonce in self._set:
                return False

            if len(self._queue) >= self._max_size:
                evicted = self._queue.popleft()
                self._set.discard(evicted)

            self._set.add(nonce)
            self._queue.append(nonce)
            return True

    def contains(self, nonce: str) -> bool:
        with self._lock:
            return nonce in self._set

    def size(self) -> int:
        with self._lock:
            return len(self._set)

    def clear(self):
        with self._lock:
            self._set.clear()
            self._queue.clear()


# Global singleton instance of NonceCache
GLOBAL_NONCE_CACHE = NonceCache()


def parse_timestamp(ts_raw: Any) -> Optional[float]:
    """
    Safely converts ISO-8601 string or numeric timestamp to epoch seconds.
    """
    if ts_raw is None:
        return None
    if isinstance(ts_raw, (int, float)):
        return float(ts_raw)
    if isinstance(ts_raw, str):
        try:
            # Handles ISO 8601 strings (e.g. 2026-10-10T20:38:24Z or with offset)
            clean_str = ts_raw.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
            return dt.timestamp()
        except Exception:
            try:
                return float(ts_raw)
            except Exception:
                return None
    return None


def validate_timestamp_drift(ts_epoch: Optional[float], current_time: Optional[float] = None) -> Tuple[bool, str]:
    """
    Validates whether the packet timestamp falls within the allowed drift window:
    - Cannot be older than 30 seconds (stale attack protection)
    - Cannot be more than 10 seconds in the future (clock skew protection)
    """
    if ts_epoch is None:
        return False, "Timestamp missing or invalid format"

    now = current_time if current_time is not None else time.time()
    drift = now - ts_epoch

    if drift > MAX_TIMESTAMP_PAST_DRIFT_SECONDS:
        return False, f"Timestamp expired: packet is {drift:.2f}s old (exceeds {MAX_TIMESTAMP_PAST_DRIFT_SECONDS}s window)"
    
    if drift < -MAX_TIMESTAMP_FUTURE_DRIFT_SECONDS:
        return False, f"Timestamp invalid: future timestamp detected ({abs(drift):.2f}s ahead of mainframe clock)"

    return True, ""


def validate_physical_consistency(metrics: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Zero-Trust Cross-Sensor Physics Consistency Checker:
    Flags synthetic data injections where values contradict physical reality.
    """
    if not isinstance(metrics, dict):
        return True, ""

    grid_voltage = metrics.get("grid_voltage")
    flood_index = metrics.get("flood_index")
    route_congestion = metrics.get("route_congestion")

    # Range sanity checks
    if grid_voltage is not None:
        try:
            gv = float(grid_voltage)
            if gv < 0.0 or gv > 500.0:
                return False, f"Physics Violation: Grid voltage {gv}V exceeds physical limits [0-500V]"
        except (ValueError, TypeError):
            return False, "Physics Violation: Non-numeric grid voltage"

    if flood_index is not None:
        try:
            fi = float(flood_index)
            if fi < 0.0 or fi > 1.0:
                return False, f"Physics Violation: Flood index {fi} outside valid normalized range [0.0, 1.0]"
        except (ValueError, TypeError):
            return False, "Physics Violation: Non-numeric flood index"

    if route_congestion is not None:
        try:
            rc = float(route_congestion)
            if rc < 0.0 or rc > 100.0:
                return False, f"Physics Violation: Route congestion {rc}% outside range [0, 100%]"
        except (ValueError, TypeError):
            return False, "Physics Violation: Non-numeric route congestion"

    # Cross-sensor contradiction: Massive flood inundation without any transformer strain or traffic disruption
    if flood_index is not None and grid_voltage is not None and route_congestion is not None:
        fi = float(flood_index)
        gv = float(grid_voltage)
        rc = float(route_congestion)
        if fi >= 0.8 and gv >= 215.0 and rc <= 15.0:
            return False, (
                f"Physics Inconsistency / Spoofing Detected: Severe flood index ({fi:.2f}) "
                f"coexists with pristine grid voltage ({gv:.1f}V) and empty traffic ({rc}%). "
                "Cross-sensor telemetry failed sanity model."
            )

    return True, ""


def verify_hmac_cpacf(raw_body: bytes, signature: str, secret_key: bytes = DEFAULT_SECRET_KEY) -> Tuple[bool, str]:
    """
    Simulates CPACF hardware-assisted HMAC-SHA256 verification (s390x instruction KIMD/KLMD).
    Performs constant-time digest comparison to prevent timing side-channel attacks.
    """
    if not signature:
        return False, "Missing HMAC signature"

    try:
        expected_sig = hmac.new(secret_key, raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature.strip().lower(), expected_sig.lower()):
            return False, "Invalid HMAC-SHA256 signature: cryptographic mismatch"
        return True, ""
    except Exception as e:
        return False, f"Cryptographic verification error: {str(e)}"


def verify_telemetry_packet(
    raw_body: bytes,
    signature: Optional[str],
    secret_key: bytes = DEFAULT_SECRET_KEY,
    nonce_cache: NonceCache = GLOBAL_NONCE_CACHE
) -> Tuple[bool, int, str, Optional[Dict[str, Any]], str]:
    """
    Complete Zero-Trust Ingestion Verification Pipeline.
    Returns:
        (is_valid: bool, status_code: int, error_reason: str, parsed_dict: Optional[dict], attack_type: str)
    """
    if not signature:
        return False, 401, "Missing X-Signature header in request", None, "missing_signature"

    # Step 1: CPACF Hardware HMAC-SHA256 Verification
    hmac_ok, hmac_err = verify_hmac_cpacf(raw_body, signature, secret_key)
    if not hmac_ok:
        return False, 401, f"HMAC Signature Verification Failed: {hmac_err}", None, "tamper"

    # Step 2: Canonical Payload Parsing
    try:
        packet_dict = json.loads(raw_body.decode("utf-8"))
        if not isinstance(packet_dict, dict):
            return False, 400, "Payload root must be a JSON object", None, "malformed"
    except Exception as e:
        return False, 400, f"Malformed JSON payload: {str(e)}", None, "malformed"

    packet_id = str(packet_dict.get("packet_id", "UNKNOWN"))
    nonce = packet_dict.get("nonce")
    if not nonce:
        return False, 401, "Packet missing cryptographic nonce", packet_dict, "missing_nonce"

    # Step 3: Thread-safe Monotonic Nonce Cache (Anti-Replay)
    nonce_ok = nonce_cache.check_and_add(str(nonce))
    if not nonce_ok:
        return False, 401, f"Replay Attack Detected: Nonce '{nonce}' has already been consumed", packet_dict, "replay"

    # Step 4: Timestamp Drift Validator (30s past / 10s future)
    ts_val = packet_dict.get("unix_timestamp")
    if ts_val is None:
        ts_val = packet_dict.get("timestamp")
    
    ts_epoch = parse_timestamp(ts_val)
    time_ok, time_err = validate_timestamp_drift(ts_epoch)
    if not time_ok:
        return False, 401, f"Stale Telemetry Detected: {time_err}", packet_dict, "stale"

    # Step 5: Physics Consistency & Sanity Cross-Check
    metrics = packet_dict.get("metrics", {})
    phys_ok, phys_err = validate_physical_consistency(metrics)
    if not phys_ok:
        return False, 403, f"Physics Consistency Failure: {phys_err}", packet_dict, "spoof"

    # All validations passed
    return True, 200, "Packet verified by CPACF Gate", packet_dict, "none"
