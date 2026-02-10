from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from .database import get_conn


def _next_unit_id(conn) -> str:
    row = conn.execute("SELECT unit_id FROM units ORDER BY unit_id DESC LIMIT 1").fetchone()
    if not row:
        return "SH-0001"
    last = row["unit_id"]  # e.g. SH-0012
    try:
        n = int(str(last).split("-")[1])
    except Exception:
        n = 0
    return f"SH-{n+1:04d}"


# =========================
# Units
# =========================
def list_units(active_only: bool = True) -> list[dict[str, Any]]:
    q = "SELECT * FROM units"
    params: tuple[Any, ...] = ()
    if active_only:
        q += " WHERE is_active=1"
    q += " ORDER BY unit_id ASC"

    with get_conn() as conn:
        rows = conn.execute(q, params).fetchall()
        data: list[dict[str, Any]] = []
        for r in rows:
            d = dict(r)
            d["photo_urls"] = json.loads(d.get("photo_urls_json") or "[]")
            data.append(d)
        return data


def get_unit(unit_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM units WHERE unit_id=?", (unit_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["photo_urls"] = json.loads(d.get("photo_urls_json") or "[]")
        return d


def create_unit(payload: dict[str, Any]) -> str:
    """
    payload keys:
      title, location, rooms, description, youtube_url, cover_image_url,
      photo_urls(list), available_from, price_day, price_week, is_active(int/bool)
    """
    with get_conn() as conn:
        unit_id = _next_unit_id(conn)

        photo_urls = payload.get("photo_urls") or []
        photo_urls_json = json.dumps(photo_urls, ensure_ascii=False)

        conn.execute(
            """
            INSERT INTO units(
              unit_id, title, location, rooms, description, youtube_url, cover_image_url, photo_urls_json,
              available_from, price_day, price_week, is_active, updated_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))
            """,
            (
                unit_id,
                payload.get("title", "").strip(),
                payload.get("location", "").strip(),
                int(payload.get("rooms") or 0),
                payload.get("description", "").strip(),
                payload.get("youtube_url", "").strip(),
                payload.get("cover_image_url", "").strip(),
                photo_urls_json,
                payload.get("available_from", "").strip(),
                payload.get("price_day", "").strip(),
                payload.get("price_week", "").strip(),
                1 if payload.get("is_active", True) else 0,
            ),
        )
        return unit_id


def update_unit(unit_id: str, payload: dict[str, Any]) -> None:
    photo_urls = payload.get("photo_urls") or []
    photo_urls_json = json.dumps(photo_urls, ensure_ascii=False)

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE units SET
              title=?,
              location=?,
              rooms=?,
              description=?,
              youtube_url=?,
              cover_image_url=?,
              photo_urls_json=?,
              available_from=?,
              price_day=?,
              price_week=?,
              is_active=?,
              updated_at=datetime('now')
            WHERE unit_id=?
            """,
            (
                payload.get("title", "").strip(),
                payload.get("location", "").strip(),
                int(payload.get("rooms") or 0),
                payload.get("description", "").strip(),
                payload.get("youtube_url", "").strip(),
                payload.get("cover_image_url", "").strip(),
                photo_urls_json,
                payload.get("available_from", "").strip(),
                payload.get("price_day", "").strip(),
                payload.get("price_week", "").strip(),
                1 if payload.get("is_active", True) else 0,
                unit_id,
            ),
        )


# =========================
# Leads
# =========================
def create_lead(
    *,
    unit_id: str,
    action: str,  # whatsapp / call / booking
    guest_name: str,
    guest_phone: str,
    guest_residence: str,
    duration_text: str = "",
    note: str = "",
    meta: dict | None = None,
) -> str:
    lead_id = str(uuid.uuid4())
    meta_json = json.dumps(meta or {}, ensure_ascii=False)

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO leads(
              lead_id, unit_id, action, duration_text, note,
              guest_name, guest_phone, guest_residence, meta_json
            )
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                lead_id,
                unit_id,
                action,
                (duration_text or "").strip(),
                (note or "").strip(),
                (guest_name or "").strip(),
                (guest_phone or "").strip(),
                (guest_residence or "").strip(),
                meta_json,
            ),
        )
    return lead_id


def list_leads(limit: int = 200) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT lead_id, created_at, unit_id, action, duration_text, note,
                   guest_name, guest_phone, guest_residence
            FROM leads
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
