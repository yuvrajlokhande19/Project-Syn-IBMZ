"""
================================================================================
Project Syn / AegisCore: Mainframe Verification & Cryptographic Unit Tests
Target: IBM LinuxONE s390x
================================================================================
Comprehensive verification suite testing:
1. CPACF Hardware HMAC-SHA256 signature verification.
2. Monotonic Nonce Cache anti-replay protections.
3. Timestamp drift boundary constraints (30s past / 10s future).
4. Cross-sensor physics sanity validation.
5. SQLite Immutable Chained Hash Ledger & Genesis-to-Head chain verification.
6. Detection of cryptographic tampering on modified blocks.
7. Dijkstra hospital rerouting engine.
8. Trilingual fallback alert generation.
================================================================================
"""

import os
import sys
import time
import json
import hmac
import hashlib
import sqlite3

# Ensure local imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_gate import (
    NonceCache,
    validate_timestamp_drift,
    validate_physical_consistency,
    verify_hmac_cpacf,
    verify_telemetry_packet,
    DEFAULT_SECRET_KEY
)
from hash_ledger import (
    init_ledger_db,
    get_last_hash,
    append_to_ledger,
    verify_ledger_chain,
    log_security_audit,
    get_security_audit_logs,
    log_alert,
    get_latest_alert,
    get_ledger_stats,
    LEDGER_DB_PATH
)
from queue_worker import compute_safe_route
from telegram_dispatch import generate_local_s390x_llm, format_alert_message


def run_tests():
    print("=" * 70)
    print("PROJECT SYN / AEGISCORE: AUTOMATED TEST SUITE")
    print("=" * 70)
    passed_count = 0
    total_count = 0

    def assert_test(condition, name):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            print(f"[PASS] Test {total_count}: {name}")
            passed_count += 1
        else:
            print(f"[FAIL] Test {total_count}: {name}")
            raise AssertionError(f"Test failed: {name}")

    # -------------------------------------------------------------
    # 1. Monotonic Nonce Cache Tests
    # -------------------------------------------------------------
    cache = NonceCache(max_size=5)
    assert_test(cache.check_and_add("nonce_1") is True, "First nonce accepted")
    assert_test(cache.check_and_add("nonce_1") is False, "Duplicate nonce rejected (Replay Prevention)")
    assert_test(cache.check_and_add("nonce_2") is True, "Second unique nonce accepted")
    
    # Test eviction
    cache.check_and_add("nonce_3")
    cache.check_and_add("nonce_4")
    cache.check_and_add("nonce_5")
    assert_test(cache.size() == 5, "Nonce cache at capacity")
    cache.check_and_add("nonce_6")
    assert_test(cache.size() == 5, "Nonce cache kept at capacity after eviction")
    assert_test(cache.contains("nonce_1") is False, "Oldest nonce evicted")
    assert_test(cache.contains("nonce_6") is True, "Newest nonce present")

    # -------------------------------------------------------------
    # 2. Timestamp Drift Validator Tests
    # -------------------------------------------------------------
    now = time.time()
    ok, _ = validate_timestamp_drift(now)
    assert_test(ok is True, "Current timestamp within drift window")

    ok, msg = validate_timestamp_drift(now - 15.0)
    assert_test(ok is True, "15-second old timestamp allowed (<= 30s)")

    ok, msg = validate_timestamp_drift(now - 35.0)
    assert_test(ok is False and "expired" in msg, "35-second old timestamp rejected (> 30s window)")

    ok, msg = validate_timestamp_drift(now + 15.0)
    assert_test(ok is False and "future" in msg, "15-second future timestamp rejected (> 10s skew)")

    # -------------------------------------------------------------
    # 3. Physics Consistency Tests
    # -------------------------------------------------------------
    ok, _ = validate_physical_consistency({"grid_voltage": 220.0, "flood_index": 0.1, "route_congestion": 30})
    assert_test(ok is True, "Nominal physics metrics accepted")

    ok, msg = validate_physical_consistency({"grid_voltage": 230.0, "flood_index": 0.95, "route_congestion": 5})
    assert_test(ok is False and "Spoofing" in msg, "Physics contradiction caught (Flood + High Volt + Empty Road)")

    ok, msg = validate_physical_consistency({"grid_voltage": -10.0, "flood_index": 0.1, "route_congestion": 30})
    assert_test(ok is False, "Negative voltage bounds violation rejected")

    # -------------------------------------------------------------
    # 4. HMAC-SHA256 CPACF Tests
    # -------------------------------------------------------------
    body = b'{"packet_id":"TEST-01","voltage":220.0}'
    sig = hmac.new(DEFAULT_SECRET_KEY, body, hashlib.sha256).hexdigest()
    ok, _ = verify_hmac_cpacf(body, sig, DEFAULT_SECRET_KEY)
    assert_test(ok is True, "Valid CPACF HMAC signature verified")

    ok, _ = verify_hmac_cpacf(body, "bad_signature_00000000000000000000000000000000", DEFAULT_SECRET_KEY)
    assert_test(ok is False, "Corrupted HMAC signature rejected")

    # -------------------------------------------------------------
    # 5. Full Pipeline Gate Tests
    # -------------------------------------------------------------
    test_packet = {
        "packet_id": "SYN-TEST-9999",
        "unix_timestamp": time.time(),
        "nonce": "unique_nonce_abc_123",
        "sensor_location": "Mayo_Hospital",
        "metrics": {"grid_voltage": 220.0, "flood_index": 0.0, "route_congestion": 20}
    }
    raw = json.dumps(test_packet).encode("utf-8")
    sig = hmac.new(DEFAULT_SECRET_KEY, raw, hashlib.sha256).hexdigest()

    ok, code, reason, parsed, attack = verify_telemetry_packet(raw, sig, DEFAULT_SECRET_KEY, cache)
    assert_test(ok is True and code == 200, "Full pipeline verifies valid packet")

    # Replay same packet
    ok2, code2, reason2, _, attack2 = verify_telemetry_packet(raw, sig, DEFAULT_SECRET_KEY, cache)
    assert_test(ok2 is False and code2 == 401 and attack2 == "replay", "Full pipeline catches replay attack")

    # -------------------------------------------------------------
    # 6. Immutable Chained Hash Ledger & Genesis Chain Verification
    # -------------------------------------------------------------
    init_ledger_db()
    chain_status = verify_ledger_chain()
    assert_test(chain_status["valid"] is True, "Genesis ledger chain initially valid")

    # Append block
    item1 = {
        "packet_id": "SYN-BLOCK-01",
        "timestamp": "2026-10-10T12:00:00Z",
        "sensor_location": "GMC_Nagpur",
        "nonce": "block_nonce_01",
        "metrics": {"flood_index": 0.05}
    }
    hash1 = append_to_ledger(item1)
    assert_test(isinstance(hash1, str) and len(hash1) == 64, "Block 1 appended with 64-char SHA256 chained hash")

    item2 = {
        "packet_id": "SYN-BLOCK-02",
        "timestamp": "2026-10-10T12:00:01Z",
        "sensor_location": "Mayo_Hospital",
        "nonce": "block_nonce_02",
        "metrics": {"flood_index": 0.10}
    }
    hash2 = append_to_ledger(item2)
    assert_test(isinstance(hash2, str) and len(hash2) == 64, "Block 2 appended with chained hash")

    # Verify entire chain
    chain_audit = verify_ledger_chain()
    assert_test(chain_audit["valid"] is True and chain_audit["blocks_checked"] >= 3,
                f"Chain integrity confirmed across {chain_audit.get('blocks_checked')} blocks")

    # -------------------------------------------------------------
    # 7. Tampering Detection Test
    # -------------------------------------------------------------
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    # Find last block id
    cursor.execute("SELECT id, payload FROM telemetry_ledger ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    target_id, target_payload = row[0], row[1]
    
    # Tamper payload in database directly
    tampered_payload = target_payload.replace("SYN-BLOCK-02", "SYN-HACKED-02")
    cursor.execute("UPDATE telemetry_ledger SET payload = ? WHERE id = ?", (tampered_payload, target_id))
    conn.commit()
    conn.close()

    # Re-verify chain: MUST DETECT TAMPERING!
    tamper_check = verify_ledger_chain()
    assert_test(tamper_check["valid"] is False and tamper_check["corrupted_block_id"] == target_id,
                f"Ledger detected cryptographic tampering at block #{target_id}!")

    # Restore database integrity
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE telemetry_ledger SET payload = ? WHERE id = ?", (target_payload, target_id))
    conn.commit()
    conn.close()

    restore_check = verify_ledger_chain()
    assert_test(restore_check["valid"] is True, "Ledger integrity restored and verified")

    # -------------------------------------------------------------
    # 8. Security Audit Logging & Alerts
    # -------------------------------------------------------------
    log_security_audit("replay", "ATTACK-99", "Replay attack detected", '{"bad":1}', 401)
    logs = get_security_audit_logs(5)
    assert_test(len(logs) > 0 and logs[0]["attack_type"] == "replay", "Security audit entry persisted")

    log_alert("AIIMS_Nagpur", "FLOOD", "Flood Warning", "satellite_api")
    latest_alert = get_latest_alert()
    assert_test(latest_alert is not None and latest_alert["location"] == "AIIMS_Nagpur", "Alert persisted")

    # -------------------------------------------------------------
    # 9. Hospital Rerouting Engine (Dijkstra)
    # -------------------------------------------------------------
    route_nominal = compute_safe_route("NOMINAL", "GMC_Nagpur")
    assert_test("AIIMS_Nagpur" in route_nominal or "Mayo_Hospital" in route_nominal,
                f"Nominal hospital route calculated: {route_nominal}")

    route_flood = compute_safe_route("FLOOD", "GMC_Nagpur")
    assert_test(len(route_flood) > 0, f"Flood avoidance route calculated: {route_flood}")

    # -------------------------------------------------------------
    # 10. Trilingual s390x Big-Endian LLM Generation
    # -------------------------------------------------------------
    trilingual_flood = generate_local_s390x_llm("FLOOD", "GMC_Nagpur", "Wardha Road")
    assert_test("[EN]" in trilingual_flood and "[HI]" in trilingual_flood and "[MR]" in trilingual_flood,
                "Trilingual local template contains EN, HI, MR sections")

    full_alert = format_alert_message(
        {"sensor_location": "Mayo_Hospital", "network_mode": "LORA_RADIO_MESH"},
        "RESOURCE_DEFICIT"
    )
    assert_test("LORA RADIO MESH" in full_alert and "PROJECT SYN" in full_alert,
                "Formatted alert renders sovereign network mode and headers")

    # -------------------------------------------------------------
    # 11. Autonomous Local AI Disaster Orchestrator (100% s390x On-Prem)
    # -------------------------------------------------------------
    from local_ai_orchestrator import LOCAL_AI_AGENT
    local_eval = LOCAL_AI_AGENT.evaluate_telemetry({
        "sensor_location": "Mayo_Hospital",
        "metrics": {
            "grid_voltage": 220.0,
            "flood_index": 0.85,
            "route_congestion": 92.0,
            "supply_chain": {"blood_units_o_neg": 5}
        }
    })
    assert_test(local_eval["triage_status"] == "CRITICAL", "Local AI autonomously detects CRITICAL status")
    assert_test(len(local_eval["autonomous_directives"]) >= 2, "Local AI issues automated multi-resource directives")
    assert_test(len(local_eval["trilingual_dispatch"]["marathi"]) > 10, "Local AI synthesizes localized Marathi dispatch")

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed_count}/{total_count} PASSED (100% SUCCESS RATE)")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
