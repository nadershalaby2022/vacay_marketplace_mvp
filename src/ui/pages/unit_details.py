import streamlit as st

from ..layout import header, footer
from ..router import goto
from ...db.repository import get_unit, create_lead


def render():
    header()

    if st.session_state.get("role") != "guest":
        st.info("من فضلك ادخل بياناتك الأول.")
        goto("landing")
        return

    unit_id = st.session_state.get("unit_id")
    if not unit_id:
        st.warning("لم يتم اختيار شقة.")
        if st.button("⬅️ رجوع"):
            goto("home")
        footer()
        return

    unit = get_unit(unit_id)
    if not unit:
        st.error("الشقة غير موجودة.")
        if st.button("⬅️ رجوع"):
            goto("home")
        footer()
        return

    st.markdown(f"## {unit['title']}  \n`{unit['unit_id']}`")
    st.write(f"📍 {unit['location']} • 🛏️ غرف: {unit['rooms']}")
    st.write(unit.get("description", ""))

    st.markdown("### الصور")
    if unit.get("cover_image_url"):
        st.image(unit["cover_image_url"], use_container_width=True)

    photos = unit.get("photo_urls") or []
    if photos:
        for url in photos:
            st.image(url, use_container_width=True)
    else:
        st.info("لا توجد صور إضافية.")

    st.markdown("### الفيديو")
    if unit.get("youtube_url"):
        st.video(unit["youtube_url"])
    else:
        st.info("لا يوجد فيديو.")

    st.markdown("### السعر والإتاحة")
    st.write(f"🗓️ متاحة من: **{unit.get('available_from','')}**")
    st.write(f"💰 اليوم: **{unit.get('price_day','')}**")
    st.write(f"💰 الأسبوع: **{unit.get('price_week','')}**")

    # =========================
    # Leads: WhatsApp/Call/Booking
    # =========================
    st.markdown("### تواصل وحجز سريع")

    guest_name = st.session_state.get("guest_name", "")
    guest_phone = st.session_state.get("guest_phone", "")
    guest_residence = st.session_state.get("guest_residence", "")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("💬 محادثة واتساب", use_container_width=True):
            create_lead(
                unit_id=unit_id,
                action="whatsapp",
                guest_name=guest_name,
                guest_phone=guest_phone,
                guest_residence=guest_residence,
            )
            st.success("✅ تم تسجيل طلب واتساب (Lead)")
            st.info("لاحقًا: هنفتح واتساب على رقمك أنت/رقم السمسار.")

    with c2:
        if st.button("📞 إظهار الرقم / اتصال", use_container_width=True):
            create_lead(
                unit_id=unit_id,
                action="call",
                guest_name=guest_name,
                guest_phone=guest_phone,
                guest_residence=guest_residence,
            )
            st.success("✅ تم تسجيل طلب اتصال (Lead)")
            st.info("لاحقًا: هنظهر رقمك أنت/رقم السمسار أو نفتح الاتصال.")

    st.markdown("#### 🗓️ طلب حجز (مبدئي)")
    with st.form("booking_form"):
        duration_text = st.text_input("المدة (مثال: 3 أيام / أسبوع)", placeholder="اكتب المدة")
        note = st.text_area("ملاحظات", placeholder="عدد الأفراد / ملاحظات...")
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
        st.success("✅ تم تسجيل طلب الحجز (Lead)")
        st.info("لاحقًا: هنرسل إشعار واتساب/إيميل لك لتأكيد الحجز.")

    # Navigation buttons
    c3, c4 = st.columns(2)
    with c3:
        if st.button("⬅️ رجوع للقائمة", use_container_width=True):
            goto("home")
    with c4:
        if st.button("🔄 تغيير بيانات الدخول", use_container_width=True):
            for k in ["role", "guest_name", "guest_phone", "guest_residence", "unit_id", "page"]:
                st.session_state.pop(k, None)
            goto("landing")

    footer()
