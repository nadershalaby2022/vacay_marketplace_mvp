import streamlit as st
from typing import Optional

PAGES = {
    "landing": "Landing",
    "home": "Home",
    "unit": "Unit Details",
    "admin": "Admin",
    "guide": "Matrouh Guide",
}

def goto(page: str, unit_id: Optional[str] = None) -> None:
    st.session_state["page"] = page
    if unit_id is not None:
        st.session_state["unit_id"] = unit_id
    else:
        st.session_state.pop("unit_id", None)

def current_page() -> str:
    return st.session_state.get("page", "landing")
