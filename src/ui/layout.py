import streamlit as st

from .router import goto


def apply_theme() -> None:
    # Revert to Streamlit default theme (no custom CSS overrides).
    return None


def header():
    apply_theme()
    left, mid, right, admin_col = st.columns([2.3, 1, 1, 1])
    with left:
        st.markdown("### Dalil Matrouh")
    with mid:
        if st.button("Home", use_container_width=True):
            goto("home")
    with right:
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            goto("landing")
    with admin_col:
        if st.button("Admin", use_container_width=True):
            goto("admin")


def footer():
    st.markdown("---")
    st.caption("Dalil Matrouh")
