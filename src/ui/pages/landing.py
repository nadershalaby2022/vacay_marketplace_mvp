import streamlit as st

from ..layout import footer, apply_theme
from ..router import goto
from ...db.repository import list_sponsor_media


def _go_user(name: str, phone: str, residence: str, role: str) -> None:
    st.session_state["role"] = role
    st.session_state["guest_name"] = (name or "ضيف").strip() or "ضيف"
    st.session_state["guest_phone"] = (phone or "").strip()
    st.session_state["guest_residence"] = (residence or "").strip()
    goto("home")


def _render_video(url: str) -> None:
    st.markdown(
        f"""
        <video style="width:100%; border-radius:12px;" autoplay muted loop playsinline controls>
          <source src="{url}">
        </video>
        """,
        unsafe_allow_html=True,
    )


def _render_image(url: str) -> None:
    st.markdown(
        f"""
        <img src="{url}" loading="lazy" referrerpolicy="no-referrer"
             style="width:100%; border-radius:12px; display:block;" />
        """,
        unsafe_allow_html=True,
    )


def _landing_ads() -> None:
    media = list_sponsor_media(active_only=True)
    if not media:
        _render_image("https://picsum.photos/seed/landing-sponsor-fallback/1400/800")
        return

    main_image = next((m for m in media if m["slot"] == "main_image"), None)
    main_video = next((m for m in media if m["slot"] == "main_video"), None)
    gallery = [m for m in media if m["slot"] == "gallery"][:4]

    if main_image and main_image.get("url"):
        _render_image(main_image["url"])
    else:
        _render_image("https://picsum.photos/seed/landing-main/1400/800")

    if main_video and main_video.get("url"):
        st.markdown("#### إعلان فيديو")
        if main_video.get("media_kind") == "video":
            _render_video(main_video["url"])
        else:
            _render_image(main_video["url"])

    if gallery:
        st.markdown("#### إعلانات سريعة")
        gcols = st.columns(2)
        for i, item in enumerate(gallery):
            with gcols[i % 2]:
                if item.get("media_kind") == "video":
                    _render_video(item["url"])
                else:
                    _render_image(item["url"])


def render():
    apply_theme()
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Aref+Ruqaa:wght@400;700&display=swap');
        .hero-title {
          text-align: center;
          font-family: 'Aref Ruqaa', serif;
          font-size: clamp(36px, 6vw, 64px);
          margin: 0.5rem 0 0.8rem 0;
          line-height: 1.1;
        }
        .login-note {
          color: #666;
          margin-bottom: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='hero-title'>دليل مطروح السياحي</div>", unsafe_allow_html=True)

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown("### تسجيل الدخول")
        st.markdown("<div class='login-note'>اختر الطريقة المناسبة</div>", unsafe_allow_html=True)

        with st.container(border=True):
            with st.form("user_login"):
                st.markdown("#### دخول مستخدم")
                name = st.text_input("الاسم", placeholder="اكتب اسمك")
                phone = st.text_input("رقم التليفون", placeholder="+2010xxxxxxxx")
                residence = st.text_input("المدينة", placeholder="مطروح / القاهرة / ...")
                ok_user = st.form_submit_button("دخول مستخدم", use_container_width=True)
            if ok_user:
                if not name.strip():
                    st.error("من فضلك اكتب الاسم.")
                elif not phone.strip():
                    st.error("من فضلك اكتب رقم التليفون.")
                else:
                    _go_user(name, phone, residence, role="user")

        with st.container(border=True):
            st.markdown("#### دخول ضيف")
            st.caption("دخول مباشر بدون إدخال بيانات")
            if st.button("دخول كضيف", use_container_width=True):
                _go_user("ضيف", "", "", role="guest")

        with st.container(border=True):
            with st.form("admin_login"):
                st.markdown("#### دخول الأدمن")
                pwd = st.text_input("كلمة السر", type="password")
                ok_admin = st.form_submit_button("دخول Admin", use_container_width=True)
            if ok_admin:
                real = st.secrets.get("admin", {}).get("password", "admin123")
                if pwd == real:
                    st.session_state["role"] = "admin"
                    st.session_state["admin_authed"] = True
                    goto("admin")
                else:
                    st.error("كلمة سر الأدمن غير صحيحة.")

    with right:
        st.markdown("### إعلانات السبونسر")
        _landing_ads()

    footer()
