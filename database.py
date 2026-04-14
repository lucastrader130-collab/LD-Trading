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
            timestamp TEXT,
            regime TEXT,
            bias_win TEXT,
            bias_wdo TEXT,
            confidence TEXT,
            raw_text TEXT,
            summary TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(timestamp, regime, bias_win, bias_wdo, confidence, raw_text, summary):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (
            timestamp, regime, bias_win, bias_wdo, confidence, raw_text, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, regime, bias_win, bias_wdo, confidence, raw_text, summary))

    conn.commit()
    conn.close()


def load_recent(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, regime, bias_win, bias_wdo, confidence, summary
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows
