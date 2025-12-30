import os
import sqlite3
from typing import Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "pharmacy.db")


def get_db_connection():
    """Return a new sqlite3 connection with row factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_medication_by_name(name: str) -> dict:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT med_id, name, active_ingredients, dosage_info, requires_prescription, stock
        FROM medications
        WHERE LOWER(name) = LOWER(?)
    """,
        (name,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "Medication not found"}

    # Normalize keys to the simpler names the rest of the app expects
    return {
        "med_id": row["med_id"],
        "name": row["name"],
        "active_ingredient": row["active_ingredients"],
        "dosage": row["dosage_info"],
        "prescription_required": bool(row["requires_prescription"]),
        "stock": row["stock"],
    }


def check_medication_stock(med_id: str) -> dict:
    conn = get_db_connection()
    cur = conn.cursor()

    # The DB stores stock on the medications table in this seed data
    cur.execute(
        """
        SELECT stock
        FROM medications
        WHERE med_id = ?
    """,
        (med_id,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "Medication not found in inventory"}

    return {"med_id": med_id, "stock": row["stock"], "in_stock": row["stock"] > 0}


def check_user_prescription(user_id: str, med_id: str) -> dict:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 1
        FROM prescriptions
        WHERE user_id = ? AND med_id = ?
    """,
        (user_id, med_id),
    )

    exists = cur.fetchone() is not None
    conn.close()

    return {"user_id": user_id, "med_id": med_id, "has_prescription": exists}

