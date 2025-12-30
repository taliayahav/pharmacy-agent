import sqlite3

DB_PATH = "data/pharmacy.db"

def get_db():
    return sqlite3.connect(DB_PATH)
