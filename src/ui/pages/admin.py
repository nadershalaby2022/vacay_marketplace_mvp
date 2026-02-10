from __future__ import annotations

import streamlit as st

from ..layout import header, footer
from ...db.repository import (
    list_units,
    create_unit,
    get_unit,
    update_unit,
    list_leads,
)


def _admin_gate() -> bool:
    """
    Admin access (simple):
    - Ask for password once per session
    - Password stored in .streamlit/secrets.toml:
        [admin]
        password="admin123"
    """
    if st.session_state.get("admin_authed"):
        return True

    st.info("🔐 دخول الأدمن")
    pwd = st.text_input("Admin Password", type="password")
    if st.button("دخول"):
        real = st.secrets.get("admin", {}).get("password", "admin123")
        if pwd == real:
            st.session_state["admin_authed"] = True
            st.success("تم الدخول ✅")
            st.rerun()
        else:
            st.error("كلمة السر غير صحيحة")
    return False


def render():
    header()

    if not _admin_gate():
        footer()
        return

    st.markdown("## ⚙️ لوحة الأدمن — إدارة الشقق (SQLite)")

    tabs = st.tabs(["➕ إضافة شقة", "✏️ تعديل شقة", "📋 كل الشقق", "📞 Leads"])

    # =========================
    # Tab 1: Add Unit
    # =========================
    with tabs[0]:
        with st.form("add_unit"):
            title = st.text_input("اسم الشقة/الشاليه")
            location = st.text_input("المكان")
            rooms = st.number_input("عدد الغرف", min_value=0, value=2, step=1)
            available_from = st.text_input("متاحة من (YYYY-MM-DD)", value="2026-06-01")
            price_day = st.text_input("سعر اليوم", value="1500")
            price_week = st.text_input("سعر الأسبوع", value="9000")
            youtube_url = st.text_input("لينك يوتيوب (Embed)", value="")
            cover_image_url = st.text_input("Cover Image URL", value="")
            photos_multiline = st.text_area("روابط الصور (كل رابط في سطر)", value="")
            description = st.text_area("الوصف الثابت", value="")

            is_active = st.checkbox("مفعل (يظهر للعميل)", value=True)

            ok = st.form_submit_button("حفظ وإضافة")

        if ok:
            photo_urls = [x.strip() for x in photos_multiline.splitlines() if x.strip()]
            new_id = create_unit(
                {
                    "title": title,
                    "location": location,
                    "rooms": rooms,
                    "description": description,
                    "youtube_url": youtube_url,
                    "cover_image_url": cover_image_url,
                    "photo_urls": photo_urls,
                    "available_from": available_from,
                    "price_day": price_day,
                    "price_week": price_week,
                    "is_active": is_active,
                }
            )
            st.success(f"✅ تم إضافة الشقة: {new_id}")
            st.caption("روح على Home وشوفها ظهرت فورًا.")
            st.rerun()

    # =========================
    # Tab 2: Edit Unit
    # =========================
    with tabs[1]:
        units = list_units(active_only=False)
        if not units:
            st.info("لا توجد شقق.")
        else:
            ids = [u["unit_id"] for u in units]
            unit_id = st.selectbox("اختر شقة للتعديل", options=ids)
            unit = get_unit(unit_id) if unit_id else None

            if unit:
                with st.form("edit_unit"):
                    title = st.text_input("اسم الشقة/الشاليه", value=unit["title"])
                    location = st.text_input("المكان", value=unit["location"])
                    rooms = st.number_input("عدد الغرف", min_value=0, value=int(unit["rooms"]), step=1)
                    available_from = st.text_input("متاحة من (YYYY-MM-DD)", value=unit.get("available_from", ""))
                    price_day = st.text_input("سعر اليوم", value=unit.get("price_day", ""))
                    price_week = st.text_input("سعر الأسبوع", value=unit.get("price_week", ""))
                    youtube_url = st.text_input("لينك يوتيوب", value=unit.get("youtube_url", ""))
                    cover_image_url = st.text_input("Cover Image URL", value=unit.get("cover_image_url", ""))
                    photos_multiline = st.text_area(
                        "روابط الصور (كل رابط في سطر)",
                        value="\n".join(unit.get("photo_urls", [])),
                        height=140,
                    )
                    description = st.text_area("الوصف الثابت", value=unit.get("description", ""), height=140)
                    is_active = st.checkbox("مفعل (يظهر للعميل)", value=bool(unit.get("is_active", 1)))

                    ok = st.form_submit_button("حفظ التعديلات")

                if ok:
                    photo_urls = [x.strip() for x in photos_multiline.splitlines() if x.strip()]
                    update_unit(
                        unit_id,
                        {
                            "title": title,
                            "location": location,
                            "rooms": rooms,
                            "description": description,
                            "youtube_url": youtube_url,
                            "cover_image_url": cover_image_url,
                            "photo_urls": photo_urls,
                            "available_from": available_from,
                            "price_day": price_day,
                            "price_week": price_week,
                            "is_active": is_active,
                        },
                    )
                    st.success("✅ تم الحفظ")
                    st.rerun()

    # =========================
    # Tab 3: Units List
    # =========================
    with tabs[2]:
        units = list_units(active_only=False)
        st.write(f"عدد الشقق: {len(units)}")
        if units:
            st.dataframe(
                [
                    {
                        "unit_id": u["unit_id"],
                        "title": u["title"],
                        "location": u["location"],
                        "rooms": u["rooms"],
                        "available_from": u.get("available_from", ""),
                        "price_day": u.get("price_day", ""),
                        "price_week": u.get("price_week", ""),
                        "active": u.get("is_active", 1),
                    }
                    for u in units
                ],
                use_container_width=True,
            )

    # =========================
    # Tab 4: Leads
    # =========================
    with tabs[3]:
        leads = list_leads(limit=300)
        st.write(f"عدد الـ Leads: {len(leads)}")
        if leads:
            st.dataframe(leads, use_container_width=True)
        else:
            st.info("لا يوجد Leads بعد. جرّب اضغط واتساب/اتصال من صفحة شقة.")

    footer()
