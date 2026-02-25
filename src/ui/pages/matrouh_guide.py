import streamlit as st

from ..layout import footer, header
from ...db.repository import list_guide_categories, list_guide_items


def _render_image(url: str) -> None:
    if (url or "").strip():
        st.image(url, use_container_width=True)
    else:
        st.image("https://picsum.photos/seed/guide-fallback/1200/800", use_container_width=True)


def render():
    header()
    st.markdown("## دليل مطروح")
    st.caption("استكشف الأنشطة والأماكن حسب الأقسام التي يضيفها الأدمن.")

    categories = list_guide_categories(active_only=True)
    items = list_guide_items(active_only=True)

    if not categories:
        st.info("لا توجد أقسام في الدليل حتى الآن.")
        footer()
        return

    by_category: dict[str, list[dict]] = {}
    for item in items:
        by_category.setdefault(item["category_id"], []).append(item)

    for cat in categories:
        st.markdown(f"### {cat['name']}")
        cat_items = by_category.get(cat["category_id"], [])
        if not cat_items:
            st.info("لا توجد عناصر داخل هذا القسم بعد.")
            continue

        cols = st.columns(3)
        for i, item in enumerate(cat_items):
            with cols[i % 3]:
                with st.container(border=True):
                    _render_image(item.get("image_url", ""))
                    st.markdown(f"**{item['name']}**")
                    if item.get("description"):
                        st.caption(item["description"])
                    if item.get("location"):
                        st.write(f"📍 {item['location']}")

    footer()
