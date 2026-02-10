from __future__ import annotations

import json

from .database import get_conn
from .repository import create_unit


def seed_if_empty() -> None:
    with get_conn() as conn:
        c = conn.execute("SELECT COUNT(*) AS c FROM units").fetchone()["c"]
    if c and int(c) > 0:
        return

    # Sample units (to see something immediately)
    create_unit(
        {
            "title": "شقة الساحل - مميزة",
            "location": "الساحل الشمالي",
            "rooms": 2,
            "description": "وصف ثابت (Seed): قريبة من البحر، مناسبة للعائلات.",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "cover_image_url": "https://via.placeholder.com/900x500.png?text=SH-0001",
            "photo_urls": [
                "https://via.placeholder.com/1200x800.png?text=SH-0001+Photo+1",
                "https://via.placeholder.com/1200x800.png?text=SH-0001+Photo+2",
            ],
            "available_from": "2026-06-01",
            "price_day": "1500",
            "price_week": "9000",
            "is_active": True,
        }
    )

    create_unit(
        {
            "title": "شاليه العين السخنة",
            "location": "العين السخنة",
            "rooms": 3,
            "description": "وصف ثابت (Seed): إطلالة جميلة وموقع ممتاز.",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "cover_image_url": "https://via.placeholder.com/900x500.png?text=SH-0002",
            "photo_urls": [
                "https://via.placeholder.com/1200x800.png?text=SH-0002+Photo+1",
            ],
            "available_from": "2026-05-15",
            "price_day": "2200",
            "price_week": "13000",
            "is_active": True,
        }
    )
