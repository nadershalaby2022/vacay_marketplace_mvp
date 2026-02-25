import streamlit as st

from src.db.database import init_db
from src.db.seed import seed_if_empty
from src.ui.router import current_page, goto
from src.ui.pages import landing, home, unit_details, admin, matrouh_guide

st.set_page_config(page_title="دليل مطروح السياحى", layout="wide")


def ensure_defaults():
    st.session_state.setdefault("page", "landing")
    st.session_state.setdefault("role", None)


def main():
    init_db()
    seed_if_empty()
    ensure_defaults()

    page = current_page()

    if page == "landing":
        landing.render()
    elif page == "home":
        home.render()
    elif page == "unit":
        unit_details.render()
    elif page == "admin":
        admin.render()
    elif page == "guide":
        matrouh_guide.render()
    else:
        goto("landing")
        landing.render()


if __name__ == "__main__":
    main()
