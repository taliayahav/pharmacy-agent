import sqlite3
import os

# Ensure DB path is the one the app expects: data/pharmacy.db relative to this file
DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ensure foreign keys are enforced
cursor.execute("PRAGMA foreign_keys = ON")

users = [
    ("u1", "Dana Levi"),
    ("u2", "Noam Cohen"),
    ("u3", "Yael Katz"),
    ("u4", "Eli Rosen"),
    ("u5", "Maya Gold"),
    ("u6", "Tom Ben"),
    ("u7", "Lior Azulay"),
    ("u8", "Shira Weiss"),
    ("u9", "Amit Bar"),
    ("u10", "Roni Halevi"),
]

medications = [
    ("m1", "Amoxicillin", "Amoxicillin", 1, "500mg every 8 hours", 42),
    ("m2", "Paracetamol", "Paracetamol", 0, "500–1000mg every 6 hours", 120),
    ("m3", "Ibuprofen", "Ibuprofen", 0, "200–400mg every 6–8 hours", 75),
    ("m4", "Azithromycin", "Azithromycin", 1, "500mg once daily", 20),
    ("m5", "Cetirizine", "Cetirizine", 0, "10mg once daily", 60),
]

# prescriptions must reference med_id now
prescriptions = [
    ("u1", "m1"),  # Amoxicillin
    ("u3", "m4"),  # Azithromycin
    ("u5", "m1"),  # Amoxicillin
]

cursor.executemany("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", users)
cursor.executemany(
    "INSERT OR IGNORE INTO medications (med_id, name, active_ingredients, requires_prescription, dosage_info, stock) VALUES (?, ?, ?, ?, ?, ?)",
    medications,
)

# insert prescriptions after users and medications
cursor.executemany("INSERT OR IGNORE INTO prescriptions (user_id, med_id) VALUES (?, ?)", prescriptions)

conn.commit()
conn.close()
