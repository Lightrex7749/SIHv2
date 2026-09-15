"""
DrishtiSetu — Database & Decision Audit Trail Storage (Member 6)
Implements append-only audit trail for authority actions and geospatial zones.
Schema Reference: DATABASE_SCHEMA.md v2 §9A
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "drishtisetu.db"


def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite schema for DrishtiSetu."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Decision Log table (Append-only audit trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decision_log (
        id TEXT PRIMARY KEY,
        habitation_id TEXT NOT NULL,
        recommendation_id TEXT,
        reviewed_by TEXT NOT NULL,
        decision TEXT NOT NULL,
        notes TEXT,
        reviewed_at TEXT NOT NULL
    )
    """)

    # Land use zones table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS land_use_zones (
        id TEXT PRIMARY KEY,
        zone_type TEXT NOT NULL,
        name TEXT NOT NULL,
        source TEXT NOT NULL,
        reason TEXT
    )
    """)

    # Seed initial demo decisions if table is empty
    cursor.execute("SELECT COUNT(*) FROM decision_log")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
        INSERT INTO decision_log (id, habitation_id, recommendation_id, reviewed_by, decision, notes, reviewed_at)
        VALUES 
        ('LOG_INIT_01', 'H001', 'REC_JOSH_01', 'District Magistrate, Chamoli', 'DEFERRED', 'Initial geological survey requested for Sunil-Manohar slope before final relocation gazette notification.', '2026-09-12T09:30:00Z'),
        ('LOG_INIT_02', 'H002', 'REC_RAINI_01', 'State Disaster Management Commissioner', 'ACCEPTED', 'Approved emergency phased transit shelter construction at Pipalkoti Tableland.', '2026-09-13T14:15:00Z')
        """)

    conn.commit()
    conn.close()


def log_authority_decision(
    habitation_id: str,
    decision: str,
    reviewed_by: str,
    recommendation_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Appends an authority action to the audit trail.
    RULE: decision_log entries are append-only.
    """
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    log_id = f"LOG_{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()
    rec_id = recommendation_id or f"REC_{habitation_id}_01"

    cursor.execute("""
    INSERT INTO decision_log (id, habitation_id, recommendation_id, reviewed_by, decision, notes, reviewed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (log_id, habitation_id, rec_id, reviewed_by, decision.upper(), notes or "", now_iso))

    conn.commit()
    conn.close()

    return {
        "id": log_id,
        "habitation_id": habitation_id,
        "recommendation_id": rec_id,
        "decision": decision.upper(),
        "reviewed_by": reviewed_by,
        "notes": notes or "",
        "reviewed_at": now_iso
    }


def get_decision_history(habitation_id: str) -> List[Dict[str, Any]]:
    """Retrieves full decision audit trail for a habitation, ordered newest first."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, habitation_id, recommendation_id, reviewed_by, decision, notes, reviewed_at
    FROM decision_log
    WHERE UPPER(habitation_id) = UPPER(?)
    ORDER BY reviewed_at DESC
    """, (habitation_id,))

    rows = cursor.fetchall()
    history = []
    for r in rows:
        history.append({
            "id": r["id"],
            "habitation_id": r["habitation_id"],
            "recommendation_id": r["recommendation_id"],
            "reviewed_by": r["reviewed_by"],
            "decision": r["decision"],
            "notes": r["notes"],
            "reviewed_at": r["reviewed_at"]
        })

    conn.close()
    return history


def get_all_decision_logs() -> List[Dict[str, Any]]:
    """Retrieves all decision logs across all habitations."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, habitation_id, recommendation_id, reviewed_by, decision, notes, reviewed_at
    FROM decision_log
    ORDER BY reviewed_at DESC
    """)
    rows = cursor.fetchall()
    history = []
    for r in rows:
        history.append({
            "id": r["id"],
            "habitation_id": r["habitation_id"],
            "recommendation_id": r["recommendation_id"],
            "reviewed_by": r["reviewed_by"],
            "decision": r["decision"],
            "notes": r["notes"],
            "reviewed_at": r["reviewed_at"]
        })
    conn.close()
    return history


# Run init on module load
init_db()
