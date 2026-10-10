"""
================================================================================
Project Syn / AegisCore: Immutable CPACF Telemetry Ledger & Audit System
Hardware Target: IBM LinuxONE s390x (CPACF Acceleration Architecture)
================================================================================
Implements an immutable cryptographic chained hash ledger and security audit log
persisted in SQLite. Includes full genesis-to-head cryptographic chain verification.
================================================================================
"""

import os
import sqlite3
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("hash_ledger")
logger.setLevel(logging.INFO)

# Absolute path to ledger database in mainframe-core
LEDGER_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ledger.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled, WAL mode, and concurrency timeout."""
    conn = sqlite3.connect(LEDGER_DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    # Enterprise crash-resilience & power-cut protection
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_ledger_db():
    """Initializes tables for telemetry ledger, security audit, and dispatch alerts."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Primary Immutable Telemetry Ledger
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                packet_id TEXT NOT NULL,
                location TEXT NOT NULL,
                payload TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                chained_hash TEXT NOT NULL,
                nonce TEXT NOT NULL,
                verified_cpacf INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Migration: Ensure all columns exist if table was created with an earlier schema
        cursor.execute("PRAGMA table_info(telemetry_ledger)")
        existing_cols = {c["name"] for c in cursor.fetchall()}
        if "chained_hash" not in existing_cols:
            cursor.execute("ALTER TABLE telemetry_ledger ADD COLUMN chained_hash TEXT")
            if "hash" in existing_cols:
                cursor.execute("UPDATE telemetry_ledger SET chained_hash = hash WHERE chained_hash IS NULL")
        if "packet_id" not in existing_cols:
            cursor.execute("ALTER TABLE telemetry_ledger ADD COLUMN packet_id TEXT DEFAULT 'UNKNOWN'")
        if "location" not in existing_cols:
            cursor.execute("ALTER TABLE telemetry_ledger ADD COLUMN location TEXT DEFAULT 'Unknown'")
        if "nonce" not in existing_cols:
            cursor.execute("ALTER TABLE telemetry_ledger ADD COLUMN nonce TEXT DEFAULT '00000000'")
        if "verified_cpacf" not in existing_cols:
            cursor.execute("ALTER TABLE telemetry_ledger ADD COLUMN verified_cpacf INTEGER DEFAULT 1")

        # 2. Security Audit Table (records all rejections and cyber attacks)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                attack_type TEXT NOT NULL,
                packet_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                raw_payload TEXT NOT NULL,
                rejected_status INTEGER NOT NULL DEFAULT 401
            )
        """)

        # 3. Emergency Alerts Dispatch Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                location TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                message TEXT NOT NULL,
                network_mode TEXT NOT NULL
            )
        """)

        # 4. Backward-compatible hash_ledger view/table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hash_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                previous_hash TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                chained_hash TEXT NOT NULL
            )
        """)

        # Genesis Block Initialization
        cursor.execute("SELECT COUNT(*) FROM telemetry_ledger")
        if cursor.fetchone()[0] == 0:
            genesis_payload = "genesis"
            genesis_data_hash = hashlib.sha256(genesis_payload.encode("utf-8")).hexdigest()
            genesis_prev_hash = "0" * 64
            genesis_chained_hash = hashlib.sha256((genesis_prev_hash + genesis_data_hash).encode("utf-8")).hexdigest()

            cursor.execute("""
                INSERT INTO telemetry_ledger (
                    timestamp, packet_id, location, payload, previous_hash, chained_hash, nonce, verified_cpacf
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "2026-10-10T00:00:00Z",
                "GENESIS-0000",
                "IBM_LinuxONE_s390x_Root",
                genesis_payload,
                genesis_prev_hash,
                genesis_chained_hash,
                "0000000000000000",
                1
            ))

            # Legacy table genesis
            cursor.execute("SELECT COUNT(*) FROM hash_ledger")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO hash_ledger (previous_hash, data_hash, chained_hash)
                    VALUES (?, ?, ?)
                """, (genesis_prev_hash, genesis_data_hash, genesis_chained_hash))

        conn.commit()
    finally:
        conn.close()


def get_last_hash() -> str:
    """Returns the most recent chained hash from the ledger."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT chained_hash FROM telemetry_ledger ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row["chained_hash"] if row else "0" * 64
    finally:
        conn.close()


def append_to_ledger(item: Dict[str, Any], verified_cpacf: int = 1) -> str:
    """
    Appends a verified telemetry packet into the immutable hash ledger.
    Calculates CPACF SHA-256 chained hash:
    chained_hash = SHA256(previous_hash + SHA256(canonical_payload))
    """
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Canonical deterministic JSON stringification
        canonical_payload = json.dumps(item, sort_keys=True, separators=(',', ':'))
        data_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

        # Fetch current head hash
        cursor.execute("SELECT chained_hash FROM telemetry_ledger ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        previous_hash = row["chained_hash"] if row else "0" * 64

        chained_input = (previous_hash + data_hash).encode("utf-8")
        chained_hash = hashlib.sha256(chained_input).hexdigest()

        timestamp = str(item.get("timestamp", datetime.now(timezone.utc).isoformat()))
        packet_id = str(item.get("packet_id", "UNKNOWN"))
        location = str(item.get("sensor_location", "Unknown"))
        nonce = str(item.get("nonce", "00000000"))

        cursor.execute("""
            INSERT INTO telemetry_ledger (
                timestamp, packet_id, location, payload, previous_hash, chained_hash, nonce, verified_cpacf
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            packet_id,
            location,
            canonical_payload,
            previous_hash,
            chained_hash,
            nonce,
            verified_cpacf
        ))

        # Backward compatibility sync
        cursor.execute("""
            INSERT INTO hash_ledger (previous_hash, data_hash, chained_hash)
            VALUES (?, ?, ?)
        """, (previous_hash, data_hash, chained_hash))

        conn.commit()
        logger.debug(f"[LEDGER] Block recorded: ID={packet_id} ChainedHash={chained_hash[:16]}...")
        return chained_hash
    except Exception as e:
        logger.error(f"[LEDGER ERROR] Failed to append block: {e}")
        raise
    finally:
        conn.close()


def log_security_audit(
    attack_type: str,
    packet_id: str,
    reason: str,
    raw_payload: str,
    rejected_status: int = 401
):
    """Logs security breaches, spoofing attempts, replay attacks, and drift violations."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        ts = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO security_audit (
                timestamp, attack_type, packet_id, reason, raw_payload, rejected_status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ts,
            attack_type,
            str(packet_id),
            str(reason),
            str(raw_payload),
            int(rejected_status)
        ))
        conn.commit()
        logger.warning(f"[SECURITY AUDIT] Attack logged: Type={attack_type} PacketID={packet_id} Reason={reason}")
    except Exception as e:
        logger.error(f"[SECURITY AUDIT ERROR] Failed to record audit: {e}")
    finally:
        conn.close()


def log_alert(location: str, anomaly_type: str, message: str, network_mode: str = "satellite_api"):
    """Persists an anomaly alert into the alerts table."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        ts = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO alerts (timestamp, location, anomaly_type, message, network_mode)
            VALUES (?, ?, ?, ?, ?)
        """, (ts, location, anomaly_type, message, network_mode))
        conn.commit()
    except Exception as e:
        logger.error(f"[ALERT LOG ERROR] Failed to persist alert: {e}")
    finally:
        conn.close()


def get_latest_alert() -> Optional[Dict[str, Any]]:
    """Fetches the latest recorded anomaly alert."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "location": row["location"],
                "anomaly_type": row["anomaly_type"],
                "message": row["message"],
                "network_mode": row["network_mode"]
            }
        return None
    finally:
        conn.close()


def verify_ledger_chain() -> Dict[str, Any]:
    """
    Cryptographic Audit Function:
    Re-hashes the ENTIRE database sequentially from Genesis Block to Head Block.
    Verifies that:
    1. Every block's previous_hash exactly equals the preceding block's chained_hash.
    2. Every block's chained_hash matches SHA256(previous_hash + SHA256(canonical_payload)).
    Returns verification pass/fail status and exact violation coordinates if tampered.
    """
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telemetry_ledger ORDER BY id ASC")
        rows = cursor.fetchall()

        if not rows:
            return {"valid": False, "blocks_checked": 0, "reason": "Ledger is empty"}

        expected_prev_hash = "0" * 64

        for index, row in enumerate(rows):
            block_id = row["id"]
            stored_prev = row["previous_hash"]
            stored_chained = row["chained_hash"]
            payload_str = row["payload"]

            # Step A: Linkage Check
            if stored_prev != expected_prev_hash:
                return {
                    "valid": False,
                    "blocks_checked": index,
                    "corrupted_block_id": block_id,
                    "reason": (
                        f"Cryptographic link broken at block #{block_id} ({row['packet_id']}). "
                        f"Expected previous_hash {expected_prev_hash[:16]}... but found {stored_prev[:16]}..."
                    ),
                    "head_hash": stored_chained
                }

            # Step B: Recompute Data Hash & Chained Hash
            computed_data_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
            computed_chained_hash = hashlib.sha256((stored_prev + computed_data_hash).encode("utf-8")).hexdigest()

            if stored_chained != computed_chained_hash:
                return {
                    "valid": False,
                    "blocks_checked": index,
                    "corrupted_block_id": block_id,
                    "reason": (
                        f"Cryptographic tampering detected in block #{block_id} payload or hash! "
                        f"Stored chained_hash {stored_chained[:16]}... != Recomputed {computed_chained_hash[:16]}..."
                    ),
                    "head_hash": stored_chained
                }

            expected_prev_hash = stored_chained

        return {
            "valid": True,
            "blocks_checked": len(rows),
            "head_hash": rows[-1]["chained_hash"],
            "genesis_hash": rows[0]["chained_hash"],
            "status": "ALL_BLOCKS_CRYPTOGRAPHICALLY_VERIFIED"
        }
    finally:
        conn.close()


def get_recent_blocks(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns the latest N blocks from the telemetry ledger."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, packet_id, location, payload, previous_hash, chained_hash, nonce, verified_cpacf
            FROM telemetry_ledger
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        blocks = []
        for r in rows:
            try:
                parsed_payload = json.loads(r["payload"]) if r["payload"] != "genesis" else {"message": "genesis"}
            except Exception:
                parsed_payload = {"raw": r["payload"]}

            blocks.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "packet_id": r["packet_id"],
                "location": r["location"],
                "payload": parsed_payload,
                "previous_hash": r["previous_hash"],
                "chained_hash": r["chained_hash"],
                "nonce": r["nonce"],
                "verified_cpacf": bool(r["verified_cpacf"])
            })
        return blocks
    finally:
        conn.close()


def get_security_audit_logs(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns recent security audit rejections."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, attack_type, packet_id, reason, raw_payload, rejected_status
            FROM security_audit
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "timestamp": r["timestamp"],
                "attack_type": r["attack_type"],
                "packet_id": r["packet_id"],
                "reason": r["reason"],
                "raw_payload": r["raw_payload"][:200] if r["raw_payload"] else "",
                "rejected_status": r["rejected_status"]
            }
            for r in rows
        ]
    finally:
        conn.close()


def get_ledger_stats() -> Dict[str, Any]:
    """Returns comprehensive ledger statistics."""
    init_ledger_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry_ledger")
        total_blocks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM security_audit")
        total_rejections = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts = cursor.fetchone()[0]

        cursor.execute("SELECT chained_hash FROM telemetry_ledger ORDER BY id DESC LIMIT 1")
        last_hash_row = cursor.fetchone()
        last_hash = last_hash_row["chained_hash"] if last_hash_row else "0" * 64

        return {
            "total_blocks": total_blocks,
            "total_rejections": total_rejections,
            "total_alerts": total_alerts,
            "last_hash": last_hash
        }
    finally:
        conn.close()
