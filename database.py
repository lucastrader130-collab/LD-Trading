import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "ld_trading.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            raw_text TEXT,
            bias TEXT,
            probability_up REAL,
            probability_down REAL,
            traps TEXT,
            summary TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_analysis(created_at, raw_text, bias, probability_up, probability_down, traps, summary):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (
            created_at, raw_text, bias, probability_up, probability_down, traps, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (created_at, raw_text, bias, probability_up, probability_down, traps, summary))

    conn.commit()
    conn.close()

def load_recent(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT created_at, bias, probability_up, probability_down, traps, summary
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows
