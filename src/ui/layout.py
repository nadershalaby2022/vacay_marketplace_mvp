import streamlit as st
from .router import goto


def header():
    left, mid, right, admin_col = st.columns([2, 1, 1, 1])

    with left:
        st.markdown("### 🏖️ Vacay Marketplace MVP")

    with mid:
        if st.button("🏠 الرئيسية", use_container_width=True):
            goto("home")

    with right:
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.clear()
            goto("landing")

    with admin_col:
        if st.button("⚙️ Admin", use_container_width=True):
            goto("admin")


def footer():
    st.markdown("---")
    st.caption("MVP • Stage 2: SQLite + Admin")
