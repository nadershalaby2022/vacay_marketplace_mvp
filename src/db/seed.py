from __future__ import annotations

import json

from .database import get_conn
from .repository import add_sponsor_media, create_unit


def seed_if_empty() -> None:
    _seed_units_if_empty()
    _seed_sponsors_if_empty()
    _backfill_missing_media_links()


def _seed_units_if_empty() -> None:
    with get_conn() as conn:
        c = conn.execute("SELECT COUNT(*) AS c FROM units").fetchone()["c"]
    if c and int(c) > 0:
        return

    create_unit(
        {
            "title": "شقة الساحل - مميزة",
            "property_type": "شقة",
            "location": "الساحل الشمالي",
            "rooms": 2,
            "description": "وصف ثابت (Seed): قريبة من البحر ومناسبة للعائلات.",
            "youtube_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "cover_image_url": "https://picsum.photos/seed/sh0001-cover/1200/800",
            "photo_urls": [
                "https://picsum.photos/seed/sh0001-1/1200/800",
                "https://picsum.photos/seed/sh0001-2/1200/800",
            ],
            "contact_whatsapp": "+201001112233",
            "contact_phone": "+201001112233",
            "available_from": "2026-06-01",
            "available_to": "2026-09-30",
            "price_day": "1500",
            "price_week": "9000",
            "is_active": True,
        }
    )

    create_unit(
        {
            "title": "شالية العين السخنة",
            "property_type": "شالية",
            "location": "العين السخنة",
            "rooms": 3,
            "description": "وصف ثابت (Seed): إطلالة جميلة وموقع ممتاز.",
            "youtube_url": "https://www.w3schools.com/html/movie.mp4",
            "cover_image_url": "https://picsum.photos/seed/sh0002-cover/1200/800",
            "photo_urls": ["https://picsum.photos/seed/sh0002-1/1200/800"],
            "contact_whatsapp": "+201001112244",
            "contact_phone": "+201001112244",
            "available_from": "2026-05-15",
            "available_to": "2026-10-15",
            "price_day": "2200",
            "price_week": "13000",
            "is_active": True,
        }
    )


def _seed_sponsors_if_empty() -> None:
    with get_conn() as conn:
        c = conn.execute("SELECT COUNT(*) AS c FROM sponsor_media").fetchone()["c"]
    if not (c and int(c) > 0):
        add_sponsor_media(
            slot="main_image",
            media_kind="image",
            title="إعلان رئيسي",
            url="https://picsum.photos/seed/s-main/1600/800",
        )
        add_sponsor_media(
            slot="main_video",
            media_kind="video",
            title="فيديو رئيسي",
            url="https://www.w3schools.com/html/mov_bbb.mp4",
        )
        for i in range(1, 8):
            add_sponsor_media(
                slot="gallery",
                media_kind="image",
                title=f"إعلان {i}",
                url=f"https://picsum.photos/seed/s-g-{i}/900/600",
            )

    _ensure_active_sponsor_slots()


def _ensure_active_sponsor_slots() -> None:
    with get_conn() as conn:
        active = conn.execute(
            "SELECT slot, COUNT(*) AS c FROM sponsor_media WHERE is_active=1 GROUP BY slot"
        ).fetchall()
    by_slot = {r["slot"]: int(r["c"]) for r in active}

    if by_slot.get("main_image", 0) == 0:
        add_sponsor_media(
            slot="main_image",
            media_kind="image",
            title="إعلان رئيسي افتراضي",
            url="https://picsum.photos/seed/s-main-fallback/1600/800",
        )
    if by_slot.get("main_video", 0) == 0:
        add_sponsor_media(
            slot="main_video",
            media_kind="video",
            title="فيديو رئيسي افتراضي",
            url="https://www.w3schools.com/html/movie.mp4",
        )
    if by_slot.get("gallery", 0) == 0:
        for i in range(1, 6):
            add_sponsor_media(
                slot="gallery",
                media_kind="image",
                title=f"إعلان جاليري {i}",
                url=f"https://picsum.photos/seed/s-g-fallback-{i}/900/600",
            )


def _backfill_missing_media_links() -> None:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT unit_id, cover_image_url, photo_urls_json, youtube_url, available_to FROM units"
        ).fetchall()
        for r in rows:
            unit_id = r["unit_id"]
            cover = (r["cover_image_url"] or "").strip()
            photos_json = r["photo_urls_json"] or "[]"
            video = (r["youtube_url"] or "").strip()
            available_to = (r["available_to"] or "").strip()

            try:
                photos = json.loads(photos_json) if photos_json else []
            except Exception:
                photos = []

            if not cover:
                cover = f"https://picsum.photos/seed/{unit_id}-cover/1200/800"
            if not photos:
                photos = [
                    f"https://picsum.photos/seed/{unit_id}-p1/1200/800",
                    f"https://picsum.photos/seed/{unit_id}-p2/1200/800",
                ]
            if not video:
                video = "https://www.w3schools.com/html/mov_bbb.mp4"
            if not available_to:
                available_to = "2026-12-31"

            conn.execute(
                """
                UPDATE units
                SET cover_image_url=?, photo_urls_json=?, youtube_url=?, available_to=?
                WHERE unit_id=?
                """,
                (cover, json.dumps(photos, ensure_ascii=False), video, available_to, unit_id),
            )
