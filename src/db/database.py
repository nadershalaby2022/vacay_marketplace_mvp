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
        property_type TEXT NOT NULL DEFAULT 'شقة',
        location TEXT NOT NULL,
        rooms INTEGER NOT NULL DEFAULT 0,
        description TEXT NOT NULL DEFAULT '',
        youtube_url TEXT NOT NULL DEFAULT '',
        cover_image_url TEXT NOT NULL DEFAULT '',
        photo_urls_json TEXT NOT NULL DEFAULT '[]',
        contact_whatsapp TEXT NOT NULL DEFAULT '',
        contact_phone TEXT NOT NULL DEFAULT '',
        available_from TEXT NOT NULL DEFAULT '',
        available_to TEXT NOT NULL DEFAULT '',
        price_day TEXT NOT NULL DEFAULT '',
        price_week TEXT NOT NULL DEFAULT '',
        is_booked INTEGER NOT NULL DEFAULT 0,
        booked_from TEXT NOT NULL DEFAULT '',
        booked_to TEXT NOT NULL DEFAULT '',
        booking_note_text TEXT NOT NULL DEFAULT '',
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS leads (
        lead_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        unit_id TEXT NOT NULL,
        action TEXT NOT NULL,
        duration_text TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '',
        guest_name TEXT NOT NULL DEFAULT '',
        guest_phone TEXT NOT NULL DEFAULT '',
        guest_residence TEXT NOT NULL DEFAULT '',
        meta_json TEXT NOT NULL DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        unit_id TEXT NOT NULL,
        guest_name TEXT NOT NULL DEFAULT '',
        guest_phone TEXT NOT NULL DEFAULT '',
        guest_residence TEXT NOT NULL DEFAULT '',
        duration_text TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'new',
        is_new_admin INTEGER NOT NULL DEFAULT 1,
        booked_from TEXT NOT NULL DEFAULT '',
        booked_to TEXT NOT NULL DEFAULT '',
        admin_schedule_text TEXT NOT NULL DEFAULT '',
        reviewed_at TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS sponsor_media (
        media_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        slot TEXT NOT NULL DEFAULT 'gallery',
        media_kind TEXT NOT NULL DEFAULT 'image',
        title TEXT NOT NULL DEFAULT '',
        url TEXT NOT NULL DEFAULT '',
        is_active INTEGER NOT NULL DEFAULT 1,
        sort_order INTEGER NOT NULL DEFAULT 0
    );
    """
    with get_conn() as conn:
        conn.executescript(ddl)
        _migrate_units_table(conn)


def _migrate_units_table(conn: sqlite3.Connection) -> None:
    unit_cols = {r["name"] for r in conn.execute("PRAGMA table_info(units)").fetchall()}
    if "property_type" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN property_type TEXT NOT NULL DEFAULT 'شقة'")
    if "contact_whatsapp" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN contact_whatsapp TEXT NOT NULL DEFAULT ''")
    if "contact_phone" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN contact_phone TEXT NOT NULL DEFAULT ''")
    if "available_to" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN available_to TEXT NOT NULL DEFAULT ''")
    if "is_booked" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN is_booked INTEGER NOT NULL DEFAULT 0")
    if "booked_from" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN booked_from TEXT NOT NULL DEFAULT ''")
    if "booked_to" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN booked_to TEXT NOT NULL DEFAULT ''")
    if "booking_note_text" not in unit_cols:
        conn.execute("ALTER TABLE units ADD COLUMN booking_note_text TEXT NOT NULL DEFAULT ''")

    booking_cols = {r["name"] for r in conn.execute("PRAGMA table_info(bookings)").fetchall()}
    if booking_cols and "reviewed_at" not in booking_cols:
        conn.execute("ALTER TABLE bookings ADD COLUMN reviewed_at TEXT NOT NULL DEFAULT ''")
