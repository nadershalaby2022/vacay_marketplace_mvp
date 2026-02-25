from urllib.parse import quote

import streamlit as st

from ..layout import footer, header
from ..router import goto
from ...db.repository import create_booking_request, create_lead, get_unit


def _normalize_phone(raw: str) -> str:
    cleaned = "".join(ch for ch in (raw or "") if ch.isdigit())
    if cleaned.startswith("00"):
        cleaned = cleaned[2:]
    return cleaned


def _wa_url(phone: str, message: str) -> str:
    return f"https://wa.me/{_normalize_phone(phone)}?text={quote(message)}"


def _render_remote_image(url: str) -> None:
    st.markdown(
        f"""
        <img src="{url}" referrerpolicy="no-referrer" loading="lazy"
             style="width:100%; border-radius:10px; display:block;" />
        """,
        unsafe_allow_html=True,
    )


def render():
    header()

    if st.session_state.get("role") not in {"guest", "user"}:
        st.info("من فضلك ادخل بياناتك الأول.")
        goto("landing")
        return

    unit_id = st.session_state.get("unit_id")
    if not unit_id:
        st.warning("لم يتم اختيار عقار.")
        if st.button("رجوع"):
            goto("home")
        footer()
        return

    unit = get_unit(unit_id)
    if not unit:
        st.error("العقار غير موجود.")
        if st.button("رجوع"):
            goto("home")
        footer()
        return

    st.markdown(f"## {unit['title']}  \n`{unit['unit_id']}`")
    st.write(f"نوع العقار: **{unit.get('property_type', 'شقة')}**")
    st.write(f"المكان: {unit['location']} - غرف: {unit['rooms']}")
    st.write(unit.get("description", ""))

    if int(unit.get("is_booked", 0)) == 1:
        st.error(
            f"تم حجز هذا العقار من {unit.get('booked_from', '-')} "
            f"إلى {unit.get('booked_to', '-')} ({unit.get('booked_days', 0)} يوم)"
        )
        if unit.get("booking_note_text"):
            st.info(unit["booking_note_text"])

    st.markdown("### الصور")
    if unit.get("cover_image_url"):
        _render_remote_image(unit["cover_image_url"])
    photos = unit.get("photo_urls") or []
    if photos:
        for p in photos:
            _render_remote_image(p)
    else:
        st.info("لا توجد صور إضافية.")

    st.markdown("### الفيديو")
    if unit.get("youtube_url"):
        st.video(unit["youtube_url"])
    else:
        st.info("لا يوجد فيديو.")

    st.markdown("### السعر والإتاحة")
    st.write(
        f"متاح من: **{unit.get('available_from', '')}** "
        f"حتى **{unit.get('available_to', '')}**"
    )
    st.write(f"اليوم: **{unit.get('price_day', '')}**")
    st.write(f"الأسبوع: **{unit.get('price_week', '')}**")

    st.markdown("### تواصل سريع")
    guest_name = st.session_state.get("guest_name", "")
    guest_phone = st.session_state.get("guest_phone", "")
    guest_residence = st.session_state.get("guest_residence", "")
    contact_whatsapp = unit.get("contact_whatsapp", "").strip()
    contact_phone = unit.get("contact_phone", "").strip()

    c1, c2 = st.columns(2)
    with c1:
        if not _normalize_phone(contact_whatsapp):
            st.warning("رقم واتساب غير مضاف لهذا العقار.")
        else:
            msg = f"مرحبًا، أريد الاستفسار عن {unit['title']} ({unit['unit_id']}). اسمي {guest_name} ورقمي {guest_phone}"
            if st.button("محادثة واتساب", use_container_width=True):
                create_lead(
                    unit_id=unit_id,
                    action="whatsapp",
                    guest_name=guest_name,
                    guest_phone=guest_phone,
                    guest_residence=guest_residence,
                )
                st.link_button("فتح واتساب الآن", _wa_url(contact_whatsapp, msg), use_container_width=True)

    with c2:
        if st.button("إظهار الرقم / اتصال", use_container_width=True):
            create_lead(
                unit_id=unit_id,
                action="call",
                guest_name=guest_name,
                guest_phone=guest_phone,
                guest_residence=guest_residence,
            )
            if contact_phone:
                st.success(f"رقم الاتصال: {contact_phone}")
                st.markdown(f"[اتصال الآن](tel:{contact_phone})")
            else:
                st.warning("رقم الاتصال غير مضاف لهذا العقار.")

    st.markdown("#### طلب حجز (مبدئي)")
    if int(unit.get("is_booked", 0)) == 1:
        st.warning("العقار محجوز حاليًا. يمكن التواصل لمعرفة أقرب فترة متاحة.")
    else:
        with st.form("booking_form"):
            duration_text = st.text_input("المدة (مثال: 3 أيام / أسبوع)")
            note = st.text_area("ملاحظات")
            ok = st.form_submit_button("إرسال طلب الحجز")

        if ok:
            create_lead(
                unit_id=unit_id,
                action="booking",
                guest_name=guest_name,
                guest_phone=guest_phone,
                guest_residence=guest_residence,
                duration_text=duration_text,
                note=note,
            )
            create_booking_request(
                unit_id=unit_id,
                guest_name=guest_name,
                guest_phone=guest_phone,
                guest_residence=guest_residence,
                duration_text=duration_text,
                note=note,
            )
            st.success("تم إرسال طلب الحجز للإدارة.")

    c3, c4 = st.columns(2)
    with c3:
        if st.button("رجوع للقائمة", use_container_width=True):
            goto("home")
    with c4:
        if st.button("تغيير بيانات الدخول", use_container_width=True):
            for k in ["role", "guest_name", "guest_phone", "guest_residence", "unit_id", "page"]:
                st.session_state.pop(k, None)
            goto("landing")

    footer()
