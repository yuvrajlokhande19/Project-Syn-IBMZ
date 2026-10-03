import sqlite3
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

LEDGER_DB_PATH = "ledger.db"

def init_ledger_db():
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hash_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            previous_hash TEXT NOT NULL,
            data_hash TEXT NOT NULL,
            chained_hash TEXT NOT NULL
        )
    """)
    
    # Initialize genesis block if empty
    cursor.execute("SELECT COUNT(*) FROM hash_ledger")
    if cursor.fetchone()[0] == 0:
        genesis_hash = hashlib.sha256(b"genesis").hexdigest()
        cursor.execute(
            "INSERT INTO hash_ledger (previous_hash, data_hash, chained_hash) VALUES (?, ?, ?)",
            ("0"*64, genesis_hash, genesis_hash)
        )
    conn.commit()
    conn.close()

def get_last_hash() -> str:
    conn = sqlite3.connect(LEDGER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT chained_hash FROM hash_ledger ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "0"*64

def append_to_ledger(data: dict):
    """
    Simulates CPACF (CP Assist for Cryptographic Function) accelerated SHA-256
    by computing a chained hash and storing it in the ledger.
    """
    try:
        init_ledger_db()
        
        data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
        data_hash = hashlib.sha256(data_bytes).hexdigest()
        
        previous_hash = get_last_hash()
        
        # Compute chained hash
        chained_input = (previous_hash + data_hash).encode('utf-8')
        chained_hash = hashlib.sha256(chained_input).hexdigest()
        
        conn = sqlite3.connect(LEDGER_DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO hash_ledger (previous_hash, data_hash, chained_hash) VALUES (?, ?, ?)",
            (previous_hash, data_hash, chained_hash)
        )
        conn.commit()
        conn.close()
        logger.debug(f"Ledger updated with hash: {chained_hash}")
        
    except Exception as e:
        logger.error(f"Error appending to ledger: {e}")
