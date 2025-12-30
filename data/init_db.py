import sqlite3
import os

# Ensure DB path is the one the app expects: data/pharmacy.db relative to this file
DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
# enable foreign key enforcement
cursor.execute("PRAGMA foreign_keys = ON")

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

# MEDICATIONS
cursor.execute("""
CREATE TABLE IF NOT EXISTS medications (
    med_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    active_ingredients TEXT,
    requires_prescription INTEGER NOT NULL DEFAULT 0,
    dosage_info TEXT,
    stock INTEGER NOT NULL DEFAULT 0
)
""")

# USER PRESCRIPTIONS
cursor.execute("""
CREATE TABLE IF NOT EXISTS prescriptions (
    user_id TEXT,
    med_id TEXT,
    PRIMARY KEY (user_id, med_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(med_id) REFERENCES medications(med_id)
)
""")

conn.commit()
conn.close()