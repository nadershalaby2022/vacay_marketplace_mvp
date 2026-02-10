import streamlit as st
from ..layout import header, footer
from ..router import goto

def render():
    # Landing: لا نعرض زر "خروج" هنا
    st.markdown("### 🏖️ Vacay Marketplace MVP")
    st.write("أول مرة دخول — (مبدئي) بالاسم + رقم الهاتف. بدون OTP الآن.")

    with st.form("guest_login"):
        name = st.text_input("الاسم", placeholder="اكتب اسمك")
        phone = st.text_input("رقم واتساب", placeholder="+2010xxxxxxxx")
        residence = st.text_input("محل الإقامة", placeholder="القاهرة / الجيزة / ...")
        ok = st.form_submit_button("دخول للتصفح")

    if ok:
        if not name.strip():
            st.error("من فضلك اكتب الاسم.")
            return
        if not phone.strip():
            st.error("من فضلك اكتب رقم واتساب.")
            return

        st.session_state["role"] = "guest"
        st.session_state["guest_name"] = name.strip()
        st.session_state["guest_phone"] = phone.strip()
        st.session_state["guest_residence"] = residence.strip()
        goto("home")

    st.markdown("---")
    st.caption("ملاحظة: OTP وإعلانات VIP هنضيفهم بعدين.")
    footer()
