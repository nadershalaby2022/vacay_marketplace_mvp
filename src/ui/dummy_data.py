DUMMY_UNITS = [
    {
        "unit_id": "SH-0001",
        "title": "شقة الساحل - مميزة",
        "location": "الساحل الشمالي",
        "rooms": 2,
        "price_day": "1500",
        "price_week": "9000",
        "available_from": "2026-06-01",
        "description": "وصف ثابت (Demo): قريبة من البحر، مناسبة للعائلات.",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "cover_image_url": "https://via.placeholder.com/900x500.png?text=SH-0001",
        "photo_urls": [
            "https://via.placeholder.com/1200x800.png?text=SH-0001+Photo+1",
            "https://via.placeholder.com/1200x800.png?text=SH-0001+Photo+2",
        ],
    },
    {
        "unit_id": "SH-0002",
        "title": "شاليه العين السخنة",
        "location": "العين السخنة",
        "rooms": 3,
        "price_day": "2200",
        "price_week": "13000",
        "available_from": "2026-05-15",
        "description": "وصف ثابت (Demo): إطلالة جميلة وموقع ممتاز.",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "cover_image_url": "https://via.placeholder.com/900x500.png?text=SH-0002",
        "photo_urls": [
            "https://via.placeholder.com/1200x800.png?text=SH-0002+Photo+1",
        ],
    },
    {
        "unit_id": "SH-0003",
        "title": "شقة الإسكندرية - سيدي بشر",
        "location": "الإسكندرية",
        "rooms": 2,
        "price_day": "1200",
        "price_week": "7000",
        "available_from": "2026-04-20",
        "description": "وصف ثابت (Demo): قريبة من الخدمات، مناسبة للأصدقاء.",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "cover_image_url": "https://via.placeholder.com/900x500.png?text=SH-0003",
        "photo_urls": [],
    },
]


def list_units():
    return DUMMY_UNITS


def get_unit(unit_id: str):
    for u in DUMMY_UNITS:
        if u["unit_id"] == unit_id:
            return u
    return None
