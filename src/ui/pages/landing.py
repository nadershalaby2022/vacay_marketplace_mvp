import streamlit as st

from ..layout import footer, apply_theme
from ..router import goto


def _go_user(name: str, phone: str, residence: str, role: str) -> None:
    st.session_state["role"] = role
    st.session_state["guest_name"] = (name or "ضيف").strip() or "ضيف"
    st.session_state["guest_phone"] = (phone or "").strip()
    st.session_state["guest_residence"] = (residence or "").strip()
    goto("home")


def render():
    apply_theme()
    st.markdown("## دليل مطروح السياحى")
    st.caption("اختار طريقة الدخول المناسبة")

    c1, c2, c3 = st.columns(3)

    with c1:
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

    with c2:
        st.markdown("#### دخول ضيف")
        st.write("دخول سريع بدون إدخال بيانات")
        if st.button("دخول كضيف", use_container_width=True):
            _go_user("ضيف", "", "", role="guest")

    with c3:
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

    footer()
