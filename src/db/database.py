from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "app.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS units (
        unit_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        location TEXT NOT NULL,
        rooms INTEGER NOT NULL DEFAULT 0,
        description TEXT NOT NULL DEFAULT '',
        youtube_url TEXT NOT NULL DEFAULT '',
        cover_image_url TEXT NOT NULL DEFAULT '',
        photo_urls_json TEXT NOT NULL DEFAULT '[]',

        available_from TEXT NOT NULL DEFAULT '',
        price_day TEXT NOT NULL DEFAULT '',
        price_week TEXT NOT NULL DEFAULT '',

        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS leads (
        lead_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),

        unit_id TEXT NOT NULL,
        action TEXT NOT NULL,             -- whatsapp / call / booking
        duration_text TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '',

        guest_name TEXT NOT NULL DEFAULT '',
        guest_phone TEXT NOT NULL DEFAULT '',
        guest_residence TEXT NOT NULL DEFAULT '',

        meta_json TEXT NOT NULL DEFAULT '{}'
    );
    """
    with get_conn() as conn:
        conn.executescript(ddl)
