import streamlit as st
from ..layout import header, footer
from ..router import goto
from ...db.repository import list_units


def render():
    header()

    if st.session_state.get("role") != "guest":
        st.info("من فضلك ادخل بياناتك الأول.")
        goto("landing")
        return

    guest_name = st.session_state.get("guest_name", "")
    st.markdown(f"## أهلاً يا **{guest_name}** 👋")
    st.write("اختر شقة لعرض التفاصيل (SQLite).")

    units = list_units(active_only=True)

    if not units:
        st.info("لا توجد شقق بعد. ادخل Admin وأضف شقق.")
        footer()
        return

    # Filters بسيطة
    locations = sorted({u["location"] for u in units})
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        loc = st.selectbox("المكان", options=["الكل"] + locations)
    with f2:
        min_rooms = st.number_input("أقل عدد غرف", min_value=0, value=0, step=1)
    with f3:
        search = st.text_input("بحث (اسم/كود)", placeholder="SH-0001")

    filtered = []
    for u in units:
        if loc != "الكل" and u["location"] != loc:
            continue
        if int(u["rooms"]) < int(min_rooms):
            continue
        if search.strip():
            s = search.strip().lower()
            if s not in u["title"].lower() and s not in u["unit_id"].lower():
                continue
        filtered.append(u)

    if not filtered:
        st.warning("لا توجد نتائج.")
        footer()
        return

    st.markdown("### الشقق")
    cols = st.columns(3)
    for i, u in enumerate(filtered):
        with cols[i % 3]:
            with st.container(border=True):
                if u.get("cover_image_url"):
                    st.image(u["cover_image_url"], use_container_width=True)
                st.markdown(f"**{u['title']}**  \n`{u['unit_id']}`")
                st.write(f"📍 {u['location']} • 🛏️ غرف: {u['rooms']}")
                st.write(f"🗓️ متاحة من: **{u.get('available_from','')}**")
                st.write(f"💰 اليوم: **{u.get('price_day','')}** • الأسبوع: **{u.get('price_week','')}**")
                if st.button("عرض التفاصيل", key=f"open_{u['unit_id']}", use_container_width=True):
                    goto("unit", unit_id=u["unit_id"])

    footer()
