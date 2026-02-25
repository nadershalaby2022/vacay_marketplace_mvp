import streamlit as st

from ..layout import header, footer
from ..router import goto
from ...db.repository import list_sponsor_media, list_units


def _render_video(url: str) -> None:
    st.markdown(
        f"""
        <video style="width:100%; border-radius:10px;" autoplay muted loop playsinline controls>
          <source src="{url}">
        </video>
        """,
        unsafe_allow_html=True,
    )


def _render_remote_image(url: str) -> None:
    st.markdown(
        f"""
        <img src="{url}" referrerpolicy="no-referrer" loading="lazy"
             style="width:100%; border-radius:10px; display:block;" />
        """,
        unsafe_allow_html=True,
    )


def _render_sponsors() -> None:
    media = list_sponsor_media(active_only=True)
    if not media:
        return

    main_image = next((m for m in media if m["slot"] == "main_image"), None)
    main_video = next((m for m in media if m["slot"] == "main_video"), None)
    gallery = [m for m in media if m["slot"] == "gallery"]

    st.markdown("### رعاة وإعلانات")
    c1, c2 = st.columns([3, 2])
    with c1:
        if main_image and main_image.get("url"):
            _render_remote_image(main_image["url"])
            if main_image.get("title"):
                st.caption(main_image["title"])
    with c2:
        if main_video and main_video.get("url"):
            if main_video.get("media_kind") == "video":
                _render_video(main_video["url"])
            else:
                _render_remote_image(main_video["url"])
            if main_video.get("title"):
                st.caption(main_video["title"])

    if gallery:
        st.markdown("#### إعلانات إضافية")
        cols = st.columns(5)
        for i, item in enumerate(gallery):
            with cols[i % 5]:
                url = item.get("url", "")
                if not url:
                    continue
                if item.get("media_kind") == "video":
                    _render_video(url)
                else:
                    _render_remote_image(url)
                if item.get("title"):
                    st.caption(item["title"])


def render():
    header()

    if st.session_state.get("role") not in {"guest", "user"}:
        st.info("من فضلك اختر طريقة الدخول أولاً.")
        goto("landing")
        return

    guest_name = st.session_state.get("guest_name", "ضيف")
    st.markdown(f"## أهلا يا **{guest_name}**")
    st.write("اختر عقار لعرض التفاصيل.")
    _render_sponsors()

    units = list_units(active_only=True)
    if not units:
        st.info("لا توجد عقارات بعد. ادخل Admin وأضف عقارات.")
        footer()
        return

    locations = sorted({u["location"] for u in units})
    property_types = sorted({u.get("property_type", "شقة") for u in units})

    f1, f2, f3, f4 = st.columns([2, 2, 1, 1])
    with f1:
        loc = st.selectbox("المكان", options=["الكل"] + locations)
    with f2:
        ptype = st.selectbox("نوع العقار", options=["الكل"] + property_types)
    with f3:
        min_rooms = st.number_input("أقل عدد غرف", min_value=0, value=0, step=1)
    with f4:
        search = st.text_input("بحث (اسم/كود)", placeholder="SH-0001")

    filtered = []
    for u in units:
        if loc != "الكل" and u["location"] != loc:
            continue
        if ptype != "الكل" and u.get("property_type", "شقة") != ptype:
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

    st.markdown("### العقارات")
    cols = st.columns(3)
    for i, u in enumerate(filtered):
        with cols[i % 3]:
            with st.container(border=True):
                if u.get("cover_image_url"):
                    _render_remote_image(u["cover_image_url"])
                st.markdown(f"**{u['title']}**  \n`{u['unit_id']}`")
                st.write(f"النوع: **{u.get('property_type', 'شقة')}**")
                st.write(f"المكان: {u['location']} - غرف: {u['rooms']}")
                if int(u.get("is_booked", 0)) == 1:
                    st.error(
                        f"محجوز من {u.get('booked_from', '-')} إلى {u.get('booked_to', '-')} "
                        f"({u.get('booked_days', 0)} يوم)"
                    )
                    if u.get("booking_note_text"):
                        st.caption(u["booking_note_text"])
                st.write(
                    f"متاح من: **{u.get('available_from', '')}** "
                    f"حتى **{u.get('available_to', '')}**"
                )
                st.write(f"اليوم: **{u.get('price_day', '')}** - الأسبوع: **{u.get('price_week', '')}**")
                if st.button("عرض التفاصيل", key=f"open_{u['unit_id']}", use_container_width=True):
                    goto("unit", unit_id=u["unit_id"])

    footer()
