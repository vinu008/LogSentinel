import sqlite3
import json
import os

DB_PATH = os.getenv("DB_PATH", "logs.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            service   TEXT NOT NULL,
            level     TEXT NOT NULL,
            message   TEXT NOT NULL,
            metadata  TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_service ON logs(service)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
    conn.commit()
    conn.close()

def insert_log(event: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO logs (timestamp, service, level, message, metadata) VALUES (?, ?, ?, ?, ?)",
        (
            event["timestamp"],
            event["service"],
            event["level"],
            event["message"],
            json.dumps(event.get("metadata")) if event.get("metadata") else None,
        ),
    )
    conn.commit()
    conn.close()
