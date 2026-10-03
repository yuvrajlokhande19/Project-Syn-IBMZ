import sqlite3
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class HashLedger:
    """
    Simulates a ledger using chained SHA-256 hashes (simulating CPACF acceleration
    on IBM LinuxONE / s390x architecture).
    """
    
    def __init__(self, db_path: str = "ledger.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    hash TEXT NOT NULL
                )
            ''')
            # Insert genesis block if empty
            cursor.execute("SELECT COUNT(*) FROM telemetry_ledger")
            if cursor.fetchone()[0] == 0:
                genesis_hash = hashlib.sha256(b"genesis").hexdigest()
                cursor.execute('''
                    INSERT INTO telemetry_ledger (timestamp, payload, previous_hash, hash)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.utcnow().isoformat(), "{}", "0" * 64, genesis_hash))
            conn.commit()

    def _get_latest_hash(self, cursor: sqlite3.Cursor) -> str:
        cursor.execute("SELECT hash FROM telemetry_ledger ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else ("0" * 64)

    def _calculate_hash(self, previous_hash: str, payload_str: str, timestamp: str) -> str:
        # In a real s390x environment, this would ideally use hardware-accelerated 
        # crypto via libica or standard libraries optimized for CPACF.
        block_data = f"{previous_hash}{payload_str}{timestamp}".encode('utf-8')
        return hashlib.sha256(block_data).hexdigest()

    def record_telemetry(self, data: Dict[str, Any]) -> str:
        payload_str = json.dumps(data, sort_keys=True)
        timestamp = datetime.utcnow().isoformat()
        
        # Use a short transaction to prevent DB locks
        with sqlite3.connect(self.db_path, isolation_level='EXCLUSIVE') as conn:
            cursor = conn.cursor()
            previous_hash = self._get_latest_hash(cursor)
            current_hash = self._calculate_hash(previous_hash, payload_str, timestamp)
            
            cursor.execute('''
                INSERT INTO telemetry_ledger (timestamp, payload, previous_hash, hash)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, payload_str, previous_hash, current_hash))
            
            conn.commit()
            
        return current_hash
