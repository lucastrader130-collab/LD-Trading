import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "ld_trading_v2.db"


def get_connection():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def get_existing_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()
    return [row[1] for row in rows]


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Cria a tabela se ainda não existir
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

    # Verifica se a estrutura atual bate com a esperada
    existing_columns = get_existing_columns(cursor, "analyses")
    expected_columns = [
        "id",
        "timestamp",
        "regime",
        "bias_win",
        "bias_wdo",
        "confidence",
        "raw_text",
        "summary",
    ]

    # Se a estrutura estiver errada, recria a tabela
    if existing_columns != expected_columns:
        cursor.execute("DROP TABLE IF EXISTS analyses")
        cursor.execute("""
            CREATE TABLE analyses (
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
