
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "ld_trading.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
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
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analyses (timestamp, regime, bias_win, bias_wdo, confidence, raw_text, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, regime, bias_win, bias_wdo, confidence, raw_text, summary))
    conn.commit()
    conn.close()

def load_recent(limit=8):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, regime, bias_win, bias_wdo, confidence, summary
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
