from __future__ import annotations

import json
import uuid
from datetime import date
from typing import Any, Optional

from .database import get_conn


def _next_unit_id(conn) -> str:
    row = conn.execute("SELECT unit_id FROM units ORDER BY unit_id DESC LIMIT 1").fetchone()
    if not row:
        return "SH-0001"
    try:
        n = int(str(row["unit_id"]).split("-")[1])
    except Exception:
        n = 0
    return f"SH-{n+1:04d}"


def _unit_days(booked_from: str, booked_to: str) -> int:
    try:
        d1 = date.fromisoformat((booked_from or "").strip())
        d2 = date.fromisoformat((booked_to or "").strip())
        return (d2 - d1).days + 1 if d2 >= d1 else 0
    except Exception:
        return 0


def _hydrate_unit(row) -> dict[str, Any]:
    d = dict(row)
    d["photo_urls"] = json.loads(d.get("photo_urls_json") or "[]")
    d["booked_days"] = _unit_days(d.get("booked_from", ""), d.get("booked_to", ""))
    return d


def list_units(active_only: bool = True) -> list[dict[str, Any]]:
    q = "SELECT * FROM units"
    if active_only:
        q += " WHERE is_active=1"
    q += " ORDER BY unit_id ASC"
    with get_conn() as conn:
        return [_hydrate_unit(r) for r in conn.execute(q).fetchall()]


def get_unit(unit_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM units WHERE unit_id=?", (unit_id,)).fetchone()
        return _hydrate_unit(row) if row else None


def create_unit(payload: dict[str, Any]) -> str:
    with get_conn() as conn:
        unit_id = _next_unit_id(conn)
        photo_urls_json = json.dumps(payload.get("photo_urls") or [], ensure_ascii=False)
        conn.execute(
            """
            INSERT INTO units(
              unit_id, title, property_type, location, rooms, description, youtube_url, cover_image_url,
              photo_urls_json, contact_whatsapp, contact_phone, available_from, available_to,
              price_day, price_week, is_active, updated_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))
            """,
            (
                unit_id,
                payload.get("title", "").strip(),
                payload.get("property_type", "شقة").strip() or "شقة",
                payload.get("location", "").strip(),
                int(payload.get("rooms") or 0),
                payload.get("description", "").strip(),
                payload.get("youtube_url", "").strip(),
                payload.get("cover_image_url", "").strip(),
                photo_urls_json,
                payload.get("contact_whatsapp", "").strip(),
                payload.get("contact_phone", "").strip(),
                payload.get("available_from", "").strip(),
                payload.get("available_to", "").strip(),
                payload.get("price_day", "").strip(),
                payload.get("price_week", "").strip(),
                1 if payload.get("is_active", True) else 0,
            ),
        )
        return unit_id


def update_unit(unit_id: str, payload: dict[str, Any]) -> None:
    photo_urls_json = json.dumps(payload.get("photo_urls") or [], ensure_ascii=False)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE units SET
              title=?, property_type=?, location=?, rooms=?, description=?,
              youtube_url=?, cover_image_url=?, photo_urls_json=?,
              contact_whatsapp=?, contact_phone=?,
              available_from=?, available_to=?, price_day=?, price_week=?,
              is_active=?, updated_at=datetime('now')
            WHERE unit_id=?
            """,
            (
                payload.get("title", "").strip(),
                payload.get("property_type", "شقة").strip() or "شقة",
                payload.get("location", "").strip(),
                int(payload.get("rooms") or 0),
                payload.get("description", "").strip(),
                payload.get("youtube_url", "").strip(),
                payload.get("cover_image_url", "").strip(),
                photo_urls_json,
                payload.get("contact_whatsapp", "").strip(),
                payload.get("contact_phone", "").strip(),
                payload.get("available_from", "").strip(),
                payload.get("available_to", "").strip(),
                payload.get("price_day", "").strip(),
                payload.get("price_week", "").strip(),
                1 if payload.get("is_active", True) else 0,
                unit_id,
            ),
        )


def set_unit_booking_status(
    *,
    unit_id: str,
    is_booked: bool,
    booked_from: str = "",
    booked_to: str = "",
    booking_note_text: str = "",
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE units
            SET is_booked=?,
                booked_from=?,
                booked_to=?,
                booking_note_text=?,
                updated_at=datetime('now')
            WHERE unit_id=?
            """,
            (
                1 if is_booked else 0,
                booked_from.strip() if is_booked else "",
                booked_to.strip() if is_booked else "",
                booking_note_text.strip() if is_booked else "",
                unit_id,
            ),
        )


def create_lead(
    *,
    unit_id: str,
    action: str,
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


def list_leads(limit: int = 300) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT lead_id, created_at, unit_id, action, duration_text, note,
                   guest_name, guest_phone, guest_residence
            FROM leads
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_all_leads() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM leads")


def delete_leads_by_guest(guest_key: str) -> int:
    v = (guest_key or "").strip()
    if not v:
        return 0
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM leads WHERE guest_name=? OR guest_phone=?",
            (v, v),
        )
        return int(cur.rowcount or 0)


def create_booking_request(
    *,
    unit_id: str,
    guest_name: str,
    guest_phone: str,
    guest_residence: str,
    duration_text: str = "",
    note: str = "",
) -> str:
    booking_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO bookings(
              booking_id, unit_id, guest_name, guest_phone, guest_residence, duration_text, note
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                booking_id,
                unit_id,
                (guest_name or "").strip(),
                (guest_phone or "").strip(),
                (guest_residence or "").strip(),
                (duration_text or "").strip(),
                (note or "").strip(),
            ),
        )
    return booking_id


def count_new_booking_requests() -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM bookings WHERE is_new_admin=1").fetchone()
        return int(row["c"] if row else 0)


def list_bookings(limit: int = 1000) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT booking_id, created_at, unit_id, guest_name, guest_phone, guest_residence,
                   duration_text, note, status, is_new_admin, booked_from, booked_to,
                   admin_schedule_text, reviewed_at
            FROM bookings
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        data = [dict(r) for r in rows]
        for d in data:
            d["booked_days"] = _unit_days(d.get("booked_from", ""), d.get("booked_to", ""))
        return data


def review_booking(
    *,
    booking_id: str,
    status: str,
    booked_from: str = "",
    booked_to: str = "",
    admin_schedule_text: str = "",
) -> None:
    clean_status = status if status in {"confirmed", "rejected"} else "rejected"
    with get_conn() as conn:
        row = conn.execute("SELECT unit_id FROM bookings WHERE booking_id=?", (booking_id,)).fetchone()
        if not row:
            return
        unit_id = row["unit_id"]

        conn.execute(
            """
            UPDATE bookings
            SET status=?, is_new_admin=0, booked_from=?, booked_to=?,
                admin_schedule_text=?, reviewed_at=datetime('now')
            WHERE booking_id=?
            """,
            (clean_status, booked_from.strip(), booked_to.strip(), admin_schedule_text.strip(), booking_id),
        )

    if clean_status == "confirmed":
        set_unit_booking_status(
            unit_id=unit_id,
            is_booked=True,
            booked_from=booked_from,
            booked_to=booked_to,
            booking_note_text=admin_schedule_text,
        )


def add_sponsor_media(*, slot: str, media_kind: str, url: str, title: str = "") -> str:
    media_id = str(uuid.uuid4())
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(sort_order), 0) AS m FROM sponsor_media WHERE slot=?",
            (slot,),
        ).fetchone()
        next_sort = int(row["m"] if row else 0) + 1
        conn.execute(
            """
            INSERT INTO sponsor_media(media_id, slot, media_kind, title, url, is_active, sort_order)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                media_id,
                (slot or "gallery").strip(),
                (media_kind or "image").strip(),
                (title or "").strip(),
                (url or "").strip(),
                1,
                next_sort,
            ),
        )
    return media_id


def update_sponsor_media(
    media_id: str,
    *,
    slot: str,
    media_kind: str,
    url: str,
    title: str = "",
    is_active: bool = True,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE sponsor_media
            SET slot=?, media_kind=?, title=?, url=?, is_active=?
            WHERE media_id=?
            """,
            (
                (slot or "gallery").strip(),
                (media_kind or "image").strip(),
                (title or "").strip(),
                (url or "").strip(),
                1 if is_active else 0,
                media_id,
            ),
        )


def list_sponsor_media(active_only: bool = True) -> list[dict[str, Any]]:
    q = "SELECT * FROM sponsor_media"
    if active_only:
        q += " WHERE is_active=1"
    q += " ORDER BY slot ASC, sort_order ASC, datetime(created_at) ASC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q).fetchall()]


def delete_sponsor_media(media_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM sponsor_media WHERE media_id=?", (media_id,))


def list_guide_categories(active_only: bool = True) -> list[dict[str, Any]]:
    q = "SELECT category_id, created_at, name, is_active, sort_order FROM guide_categories"
    if active_only:
        q += " WHERE is_active=1"
    q += " ORDER BY sort_order ASC, datetime(created_at) ASC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q).fetchall()]


def create_guide_category(name: str, is_active: bool = True) -> str:
    category_id = str(uuid.uuid4())
    with get_conn() as conn:
        row = conn.execute("SELECT COALESCE(MAX(sort_order), 0) AS m FROM guide_categories").fetchone()
        next_sort = int(row["m"] if row else 0) + 1
        conn.execute(
            """
            INSERT INTO guide_categories(category_id, name, is_active, sort_order)
            VALUES(?,?,?,?)
            """,
            (category_id, (name or "").strip(), 1 if is_active else 0, next_sort),
        )
    return category_id


def update_guide_category(category_id: str, name: str, is_active: bool = True) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE guide_categories SET name=?, is_active=? WHERE category_id=?",
            ((name or "").strip(), 1 if is_active else 0, category_id),
        )


def delete_guide_category(category_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM guide_items WHERE category_id=?", (category_id,))
        conn.execute("DELETE FROM guide_categories WHERE category_id=?", (category_id,))


def list_guide_items(active_only: bool = True) -> list[dict[str, Any]]:
    q = """
    SELECT i.item_id, i.created_at, i.category_id, c.name AS category_name,
           i.name, i.description, i.location, i.image_url, i.is_active
    FROM guide_items i
    LEFT JOIN guide_categories c ON c.category_id = i.category_id
    """
    if active_only:
        q += " WHERE i.is_active=1 AND c.is_active=1"
    q += " ORDER BY c.sort_order ASC, c.name ASC, datetime(i.created_at) ASC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q).fetchall()]


def create_guide_item(
    *,
    category_id: str,
    name: str,
    description: str = "",
    location: str = "",
    image_url: str = "",
    is_active: bool = True,
) -> str:
    item_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO guide_items(item_id, category_id, name, description, location, image_url, is_active)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                item_id,
                (category_id or "").strip(),
                (name or "").strip(),
                (description or "").strip(),
                (location or "").strip(),
                (image_url or "").strip(),
                1 if is_active else 0,
            ),
        )
    return item_id


def update_guide_item(
    item_id: str,
    *,
    category_id: str,
    name: str,
    description: str = "",
    location: str = "",
    image_url: str = "",
    is_active: bool = True,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE guide_items
            SET category_id=?, name=?, description=?, location=?, image_url=?, is_active=?
            WHERE item_id=?
            """,
            (
                (category_id or "").strip(),
                (name or "").strip(),
                (description or "").strip(),
                (location or "").strip(),
                (image_url or "").strip(),
                1 if is_active else 0,
                item_id,
            ),
        )


def delete_guide_item(item_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM guide_items WHERE item_id=?", (item_id,))
