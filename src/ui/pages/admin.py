from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from ..layout import footer, header
from ...db.repository import (
    add_sponsor_media,
    count_new_booking_requests,
    create_unit,
    delete_all_leads,
    delete_leads_by_guest,
    delete_sponsor_media,
    get_unit,
    list_bookings,
    list_leads,
    list_sponsor_media,
    list_units,
    list_guide_categories,
    list_guide_items,
    review_booking,
    set_unit_booking_status,
    update_sponsor_media,
    create_guide_category,
    update_guide_category,
    delete_guide_category,
    create_guide_item,
    update_guide_item,
    delete_guide_item,
    update_unit,
)

PROPERTY_TYPES = ["شقة", "منزل", "فيلا", "شالية", "محل تجاري", "مخزن", "اخرى"]
SPONSOR_SLOTS = ["main_image", "main_video", "gallery"]
SPONSOR_KINDS = ["image", "video", "gif"]


def _admin_gate() -> bool:
    if st.session_state.get("admin_authed"):
        return True
    st.info("دخول الأدمن")
    pwd = st.text_input("Admin Password", type="password")
    if st.button("دخول"):
        real = st.secrets.get("admin", {}).get("password", "admin123")
        if pwd == real:
            st.session_state["admin_authed"] = True
            st.success("تم الدخول بنجاح")
            st.rerun()
        else:
            st.error("كلمة السر غير صحيحة")
    return False


def _play_bell_once(new_count: int) -> None:
    last = st.session_state.get("last_new_booking_count", 0)
    should_ring = new_count > 0 and new_count > int(last)
    st.session_state["last_new_booking_count"] = new_count
    if not should_ring:
        return
    components.html(
        """
        <script>
        (function () {
          try {
            const Ctx = window.AudioContext || window.webkitAudioContext;
            const ctx = new Ctx();
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = "triangle";
            o.frequency.value = 1100;
            o.connect(g);
            g.connect(ctx.destination);
            g.gain.setValueAtTime(0.0001, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.15, ctx.currentTime + 0.01);
            o.start();
            g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35);
            o.stop(ctx.currentTime + 0.36);
          } catch (e) {}
        })();
        </script>
        """,
        height=0,
    )


def _render_new_booking_card(b: dict, units_by_id: dict[str, dict]) -> None:
    unit = units_by_id.get(b["unit_id"], {})
    with st.container(border=True):
        st.markdown(f"### طلب حجز جديد - {b['booking_id'][:8]}")
        st.write(f"تاريخ الطلب: {b['created_at']}")
        st.write(f"العقار: {unit.get('title', 'غير معروف')} (`{b['unit_id']}`)")
        st.write(f"العميل: {b.get('guest_name', '')} - {b.get('guest_phone', '')}")
        st.write(f"المدينة: {b.get('guest_residence', '')}")
        st.write(f"المدة المطلوبة: {b.get('duration_text', '')}")
        st.write(f"ملاحظات العميل: {b.get('note', '')}")

        k = b["booking_id"]
        booked_from = st.text_input("محجوز من", key=f"from_{k}", placeholder="YYYY-MM-DD")
        booked_to = st.text_input("محجوز إلى", key=f"to_{k}", placeholder="YYYY-MM-DD")
        schedule_text = st.text_input("نص الجدول الظاهر للعميل", key=f"txt_{k}")
        confirmed = st.checkbox("تم تأكيد الحجز", key=f"ok_{k}", value=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("حفظ القرار", key=f"save_{k}", use_container_width=True):
                review_booking(
                    booking_id=k,
                    status="confirmed" if confirmed else "rejected",
                    booked_from=booked_from,
                    booked_to=booked_to,
                    admin_schedule_text=schedule_text,
                )
                st.success("تم حفظ القرار.")
                st.rerun()
        with c2:
            if st.button("رفض / إغلاق", key=f"reject_{k}", use_container_width=True):
                review_booking(booking_id=k, status="rejected")
                st.warning("تم رفض الطلب.")
                st.rerun()


def render():
    header()
    if not _admin_gate():
        footer()
        return

    new_count = count_new_booking_requests()
    if new_count > 0:
        st.warning(f"يوجد {new_count} طلب حجز جديد")
    else:
        st.success("لا يوجد طلبات حجز جديدة")
    _play_bell_once(new_count)

    st.markdown("## لوحة الأدمن - إدارة العقارات والحجوزات والإعلانات")
    tabs = st.tabs(["إضافة عقار", "تعديل عقار", "كل العقارات", "الحجوزات", "إعلانات السبونسر", "دليل مطروح", "Leads"])

    with tabs[0]:
        with st.form("add_unit"):
            title = st.text_input("اسم العقار")
            property_type = st.selectbox("نوع العقار", options=PROPERTY_TYPES, index=0)
            location = st.text_input("المكان")
            rooms = st.number_input("عدد الغرف", min_value=0, value=2, step=1)
            available_from = st.text_input("متاح من (YYYY-MM-DD)", value="2026-06-01")
            available_to = st.text_input("متاح حتى (YYYY-MM-DD)", value="2026-09-30")
            price_day = st.text_input("سعر اليوم", value="1500")
            price_week = st.text_input("سعر الأسبوع", value="9000")
            contact_whatsapp = st.text_input("رقم واتساب العقار", placeholder="+2010xxxxxxxx")
            contact_phone = st.text_input("رقم الاتصال بالعقار", placeholder="+2010xxxxxxxx")
            youtube_url = st.text_input("لينك فيديو", value="https://www.w3schools.com/html/mov_bbb.mp4")
            cover_image_url = st.text_input("لينك صورة الغلاف")
            photos_multiline = st.text_area("روابط الصور (كل رابط في سطر)")
            description = st.text_area("وصف العقار")
            is_active = st.checkbox("مفعل", value=True)
            ok = st.form_submit_button("حفظ وإضافة")
        if ok:
            create_unit(
                {
                    "title": title,
                    "property_type": property_type,
                    "location": location,
                    "rooms": rooms,
                    "description": description,
                    "youtube_url": youtube_url,
                    "cover_image_url": cover_image_url,
                    "photo_urls": [x.strip() for x in photos_multiline.splitlines() if x.strip()],
                    "contact_whatsapp": contact_whatsapp,
                    "contact_phone": contact_phone,
                    "available_from": available_from,
                    "available_to": available_to,
                    "price_day": price_day,
                    "price_week": price_week,
                    "is_active": is_active,
                }
            )
            st.success("تمت إضافة العقار.")
            st.rerun()

    with tabs[1]:
        units = list_units(active_only=False)
        if units:
            unit_id = st.selectbox("اختر عقار للتعديل", options=[u["unit_id"] for u in units])
            unit = get_unit(unit_id)
            if unit:
                default_idx = PROPERTY_TYPES.index(unit.get("property_type", "شقة")) if unit.get("property_type") in PROPERTY_TYPES else 0
                with st.form("edit_unit"):
                    title = st.text_input("اسم العقار", value=unit["title"])
                    property_type = st.selectbox("نوع العقار", options=PROPERTY_TYPES, index=default_idx)
                    location = st.text_input("المكان", value=unit["location"])
                    rooms = st.number_input("عدد الغرف", min_value=0, value=int(unit["rooms"]), step=1)
                    available_from = st.text_input("متاح من (YYYY-MM-DD)", value=unit.get("available_from", ""))
                    available_to = st.text_input("متاح حتى (YYYY-MM-DD)", value=unit.get("available_to", ""))
                    price_day = st.text_input("سعر اليوم", value=unit.get("price_day", ""))
                    price_week = st.text_input("سعر الأسبوع", value=unit.get("price_week", ""))
                    contact_whatsapp = st.text_input("رقم واتساب العقار", value=unit.get("contact_whatsapp", ""))
                    contact_phone = st.text_input("رقم الاتصال بالعقار", value=unit.get("contact_phone", ""))
                    youtube_url = st.text_input("لينك فيديو", value=unit.get("youtube_url", ""))
                    cover_image_url = st.text_input("لينك صورة الغلاف", value=unit.get("cover_image_url", ""))
                    photos_multiline = st.text_area("روابط الصور (كل رابط في سطر)", value="\n".join(unit.get("photo_urls", [])))
                    description = st.text_area("وصف العقار", value=unit.get("description", ""))
                    is_active = st.checkbox("مفعل", value=bool(unit.get("is_active", 1)))
                    save = st.form_submit_button("حفظ التعديلات")
                if save:
                    update_unit(
                        unit_id,
                        {
                            "title": title,
                            "property_type": property_type,
                            "location": location,
                            "rooms": rooms,
                            "description": description,
                            "youtube_url": youtube_url,
                            "cover_image_url": cover_image_url,
                            "photo_urls": [x.strip() for x in photos_multiline.splitlines() if x.strip()],
                            "contact_whatsapp": contact_whatsapp,
                            "contact_phone": contact_phone,
                            "available_from": available_from,
                            "available_to": available_to,
                            "price_day": price_day,
                            "price_week": price_week,
                            "is_active": is_active,
                        },
                    )
                    st.success("تم الحفظ")
                    st.rerun()
        else:
            st.info("لا توجد عقارات.")

    with tabs[2]:
        units = list_units(active_only=False)
        st.write(f"عدد العقارات: {len(units)}")
        if units:
            st.dataframe(units, use_container_width=True)

    with tabs[3]:
        units = list_units(active_only=False)
        units_by_id = {u["unit_id"]: u for u in units}
        bookings = list_bookings(limit=1000)
        new_bookings = [b for b in bookings if int(b.get("is_new_admin", 0)) == 1]
        old_bookings = [b for b in bookings if int(b.get("is_new_admin", 0)) == 0]

        st.markdown(f"### حجوزات جديدة ({len(new_bookings)})")
        if new_bookings:
            for b in new_bookings:
                _render_new_booking_card(b, units_by_id)
        else:
            st.info("لا يوجد حجوزات جديدة.")

        st.markdown("---")
        st.markdown("### إدارة الحجز الحالي للعقار (إلغاء/تمديد)")
        if units:
            chosen_id = st.selectbox("اختر عقار", options=[u["unit_id"] for u in units], key="manage_booking_unit")
            cu = get_unit(chosen_id) or {}
            is_booked = st.checkbox("العقار محجوز", value=bool(int(cu.get("is_booked", 0))), key="manage_booked")
            b_from = st.text_input("من تاريخ", value=cu.get("booked_from", ""), key="manage_bfrom")
            b_to = st.text_input("إلى تاريخ", value=cu.get("booked_to", ""), key="manage_bto")
            b_note = st.text_input("نص يظهر للعميل", value=cu.get("booking_note_text", ""), key="manage_bnote")
            if st.button("حفظ حالة الحجز الحالية"):
                set_unit_booking_status(
                    unit_id=chosen_id,
                    is_booked=is_booked,
                    booked_from=b_from,
                    booked_to=b_to,
                    booking_note_text=b_note,
                )
                st.success("تم تحديث حالة الحجز.")
                st.rerun()

        st.markdown("---")
        st.markdown("### سجل الحجوزات")
        if old_bookings:
            st.dataframe(old_bookings, use_container_width=True)
        else:
            st.info("لا يوجد سجل حجوزات.")

    with tabs[4]:
        st.markdown("### إدارة إعلانات السبونسر")
        with st.form("add_sponsor_media"):
            slot = st.selectbox("مكان الإعلان", options=SPONSOR_SLOTS, index=2)
            media_kind = st.selectbox("نوع الوسيط", options=SPONSOR_KINDS, index=0)
            title = st.text_input("عنوان اختياري")
            url = st.text_input("لينك الصورة/الفيديو/GIF")
            add = st.form_submit_button("إضافة إعلان")
        if add:
            if not url.strip():
                st.error("من فضلك أدخل لينك.")
            else:
                add_sponsor_media(slot=slot, media_kind=media_kind, url=url, title=title)
                st.success("تمت إضافة الإعلان.")
                st.rerun()

        media = list_sponsor_media(active_only=False)
        active_media = [m for m in media if int(m.get("is_active", 1)) == 1]
        inactive_media = [m for m in media if int(m.get("is_active", 1)) == 0]
        st.write(f"إجمالي الوسائط: {len(media)} | النشطة: {len(active_media)} | المعطلة: {len(inactive_media)}")

        if media:
            c1, c2, c3 = st.columns(3)
            with c1:
                if active_media:
                    disable_id = st.selectbox("اختيار إعلان لتعطيله", options=[m["media_id"] for m in active_media], key="sp_disable_id")
                    if st.button("تعطيل الإعلان", use_container_width=True):
                        cur = next((m for m in media if m["media_id"] == disable_id), None)
                        if cur:
                            update_sponsor_media(
                                disable_id,
                                slot=cur["slot"],
                                media_kind=cur["media_kind"],
                                url=cur.get("url", ""),
                                title=cur.get("title", ""),
                                is_active=False,
                            )
                            st.warning("تم تعطيل الإعلان.")
                            st.rerun()
                else:
                    st.info("لا يوجد إعلان نشط.")
            with c2:
                if inactive_media:
                    enable_id = st.selectbox("اختيار إعلان لإعادة التفعيل", options=[m["media_id"] for m in inactive_media], key="sp_enable_id")
                    if st.button("إعادة تفعيل الإعلان", use_container_width=True):
                        cur = next((m for m in media if m["media_id"] == enable_id), None)
                        if cur:
                            update_sponsor_media(
                                enable_id,
                                slot=cur["slot"],
                                media_kind=cur["media_kind"],
                                url=cur.get("url", ""),
                                title=cur.get("title", ""),
                                is_active=True,
                            )
                            st.success("تمت إعادة التفعيل.")
                            st.rerun()
                else:
                    st.info("لا يوجد إعلان معطل.")
            with c3:
                del_id = st.selectbox("اختيار إعلان لحذفه نهائيًا", options=[m["media_id"] for m in media], key="sp_delete_id")
                if st.button("حذف الإعلان نهائيًا", use_container_width=True):
                    delete_sponsor_media(del_id)
                    st.error("تم حذف الإعلان نهائيًا.")
                    st.rerun()

            st.markdown("---")
            edit_id = st.selectbox("اختيار وسيط للتعديل", options=[m["media_id"] for m in media], key="sp_edit_id")
            cur = next((m for m in media if m["media_id"] == edit_id), None)
            if cur:
                e1, e2 = st.columns(2)
                with e1:
                    e_slot = st.selectbox("مكان الوسيط", options=SPONSOR_SLOTS, index=SPONSOR_SLOTS.index(cur["slot"]) if cur["slot"] in SPONSOR_SLOTS else 2)
                    e_kind = st.selectbox("نوع الوسيط", options=SPONSOR_KINDS, index=SPONSOR_KINDS.index(cur["media_kind"]) if cur["media_kind"] in SPONSOR_KINDS else 0)
                with e2:
                    e_title = st.text_input("العنوان", value=cur.get("title", ""))
                    e_url = st.text_input("اللينك", value=cur.get("url", ""))
                e_active = st.checkbox("نشط", value=bool(int(cur.get("is_active", 1))))
                if st.button("حفظ تعديل الوسيط", use_container_width=True):
                    update_sponsor_media(
                        edit_id,
                        slot=e_slot,
                        media_kind=e_kind,
                        url=e_url,
                        title=e_title,
                        is_active=e_active,
                    )
                    st.success("تم تعديل الوسيط.")
                    st.rerun()

            st.markdown("---")
            st.dataframe(media, use_container_width=True)
        else:
            st.info("لا توجد وسائط حالياً.")

    with tabs[5]:
        st.markdown("### إدارة دليل مطروح")

        categories = list_guide_categories(active_only=False)
        items = list_guide_items(active_only=False)
        st.write(f"عدد الأقسام: {len(categories)} | عدد العناصر: {len(items)}")

        with st.container(border=True):
            st.markdown("#### إضافة قسم جديد")
            new_cat_name = st.text_input("اسم القسم", key="guide_new_cat_name")
            new_cat_active = st.checkbox("القسم نشط", value=True, key="guide_new_cat_active")
            if st.button("إضافة القسم", key="guide_add_cat_btn"):
                if not new_cat_name.strip():
                    st.error("من فضلك اكتب اسم القسم.")
                else:
                    create_guide_category(new_cat_name, is_active=new_cat_active)
                    st.success("تمت إضافة القسم.")
                    st.rerun()

        if categories:
            with st.container(border=True):
                st.markdown("#### تعديل/حذف قسم")
                cat_id = st.selectbox(
                    "اختر القسم",
                    options=[c["category_id"] for c in categories],
                    format_func=lambda cid: next((c["name"] for c in categories if c["category_id"] == cid), cid),
                    key="guide_edit_cat_id",
                )
                current_cat = next((c for c in categories if c["category_id"] == cat_id), None)
                if current_cat:
                    cat_name = st.text_input("اسم القسم", value=current_cat.get("name", ""), key="guide_edit_cat_name")
                    cat_active = st.checkbox("القسم نشط", value=bool(int(current_cat.get("is_active", 1))), key="guide_edit_cat_active")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("حفظ تعديل القسم", key="guide_update_cat_btn", use_container_width=True):
                            if not cat_name.strip():
                                st.error("اسم القسم مطلوب.")
                            else:
                                update_guide_category(cat_id, cat_name, is_active=cat_active)
                                st.success("تم تعديل القسم.")
                                st.rerun()
                    with c2:
                        if st.button("حذف القسم نهائيًا", key="guide_delete_cat_btn", use_container_width=True):
                            delete_guide_category(cat_id)
                            st.warning("تم حذف القسم وكل عناصره.")
                            st.rerun()

        with st.container(border=True):
            st.markdown("#### إضافة عنصر جديد داخل قسم")
            active_categories = [c for c in categories if int(c.get("is_active", 1)) == 1]
            if not active_categories:
                st.info("أضف قسمًا نشطًا أولاً.")
            else:
                add_item_cat = st.selectbox(
                    "القسم",
                    options=[c["category_id"] for c in active_categories],
                    format_func=lambda cid: next((c["name"] for c in active_categories if c["category_id"] == cid), cid),
                    key="guide_add_item_cat",
                )
                add_item_name = st.text_input("اسم العنصر", key="guide_add_item_name")
                add_item_desc = st.text_area("وصف", key="guide_add_item_desc")
                add_item_loc = st.text_input("الموقع", key="guide_add_item_loc")
                add_item_img = st.text_input("لينك الصورة", key="guide_add_item_img")
                add_item_active = st.checkbox("العنصر نشط", value=True, key="guide_add_item_active")
                if st.button("إضافة العنصر", key="guide_add_item_btn"):
                    if not add_item_name.strip():
                        st.error("اسم العنصر مطلوب.")
                    else:
                        create_guide_item(
                            category_id=add_item_cat,
                            name=add_item_name,
                            description=add_item_desc,
                            location=add_item_loc,
                            image_url=add_item_img,
                            is_active=add_item_active,
                        )
                        st.success("تمت إضافة العنصر.")
                        st.rerun()

        if items:
            with st.container(border=True):
                st.markdown("#### تعديل/حذف عنصر")
                item_id = st.selectbox(
                    "اختر العنصر",
                    options=[i["item_id"] for i in items],
                    format_func=lambda iid: next((f"{it['name']} - {it.get('category_name','')}" for it in items if it["item_id"] == iid), iid),
                    key="guide_edit_item_id",
                )
                current_item = next((i for i in items if i["item_id"] == item_id), None)
                if current_item and categories:
                    edit_item_cat = st.selectbox(
                        "القسم",
                        options=[c["category_id"] for c in categories],
                        index=[c["category_id"] for c in categories].index(current_item["category_id"]) if current_item["category_id"] in [c["category_id"] for c in categories] else 0,
                        format_func=lambda cid: next((c["name"] for c in categories if c["category_id"] == cid), cid),
                        key="guide_edit_item_cat",
                    )
                    edit_item_name = st.text_input("اسم العنصر", value=current_item.get("name", ""), key="guide_edit_item_name")
                    edit_item_desc = st.text_area("وصف", value=current_item.get("description", ""), key="guide_edit_item_desc")
                    edit_item_loc = st.text_input("الموقع", value=current_item.get("location", ""), key="guide_edit_item_loc")
                    edit_item_img = st.text_input("لينك الصورة", value=current_item.get("image_url", ""), key="guide_edit_item_img")
                    edit_item_active = st.checkbox("العنصر نشط", value=bool(int(current_item.get("is_active", 1))), key="guide_edit_item_active")

                    e1, e2 = st.columns(2)
                    with e1:
                        if st.button("حفظ تعديل العنصر", key="guide_update_item_btn", use_container_width=True):
                            if not edit_item_name.strip():
                                st.error("اسم العنصر مطلوب.")
                            else:
                                update_guide_item(
                                    item_id,
                                    category_id=edit_item_cat,
                                    name=edit_item_name,
                                    description=edit_item_desc,
                                    location=edit_item_loc,
                                    image_url=edit_item_img,
                                    is_active=edit_item_active,
                                )
                                st.success("تم تعديل العنصر.")
                                st.rerun()
                    with e2:
                        if st.button("حذف العنصر نهائيًا", key="guide_delete_item_btn", use_container_width=True):
                            delete_guide_item(item_id)
                            st.warning("تم حذف العنصر.")
                            st.rerun()

        st.markdown("---")
        if categories:
            st.markdown("#### جدول الأقسام")
            st.dataframe(categories, use_container_width=True)
        if items:
            st.markdown("#### جدول عناصر الدليل")
            st.dataframe(items, use_container_width=True)

    with tabs[6]:
        leads = list_leads(limit=500)
        st.write(f"عدد الـ Leads: {len(leads)}")
        l1, l2 = st.columns(2)
        with l1:
            if st.button("مسح كل الـ Leads"):
                delete_all_leads()
                st.warning("تم مسح كل الـ Leads.")
                st.rerun()
        with l2:
            guest_key = st.text_input("مسح Leads لاسم أو رقم مستخدم")
            if st.button("مسح للمستخدم المحدد"):
                n = delete_leads_by_guest(guest_key)
                st.warning(f"تم مسح {n} Lead.")
                st.rerun()
        if leads:
            st.dataframe(leads, use_container_width=True)
        else:
            st.info("لا يوجد Leads.")

    footer()
