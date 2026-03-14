from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES,
)
client = gspread.authorize(creds)

ROUTINE_SECTIONS = [
    ("morning", "empowering_morning_routine", "empowering_morning_routine", "Morning Routine", "☀️"),
    ("evening", "empowering_evening_routine", "empowering_evening_routine", "Evening Routine", "🌙"),
    ("other", "daily_empowering_habits", "daily_empowering_habits", "Other", "⭐"),
]

today = date.today()
today_str = today.strftime("%Y-%m-%d")


def get_checklist_key(section_id):
    return f"daily_checklist_{section_id}_{today_str}"


def get_df_key(section_id):
    return f"routine_df_{section_id}"


def render_section(client, section_id, sheet_name, column_name, section_label, icon):
    ws = client.open(sheet_name).sheet1
    df_key = get_df_key(section_id)
    checklist_key = get_checklist_key(section_id)
    if df_key not in st.session_state:
        st.session_state[df_key] = pd.DataFrame(ws.get_all_records())
    if checklist_key not in st.session_state:
        st.session_state[checklist_key] = {}

    show_mgmt_key = f"show_management_{section_id}"
    if st.session_state.pop(f"_clear_new_input_{section_id}", None):
        st.session_state[f"new_input_{section_id}"] = ""
    if st.session_state.pop(f"_clear_new_input_empty_{section_id}", None):
        st.session_state[f"new_input_empty_{section_id}"] = ""

    st.subheader(f"{icon} {section_label}")
    df = st.session_state[df_key]
    checklist = st.session_state[checklist_key]
    show_management = st.session_state.get(show_mgmt_key, False)

    if not df.empty:
        for idx, row in df.iterrows():
            item_key = f"item_{section_id}_{idx}"
            item_name = str(row.get(column_name, "")).strip()
            if not item_name:
                continue
            if show_management:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    checked = st.checkbox(
                        item_name,
                        value=checklist.get(item_key, False),
                        key=f"check_{item_key}_{today_str}",
                    )
                    checklist[item_key] = checked
                with col2:
                    if st.button("✏️", key=f"edit_{section_id}_{idx}", help="Edit", use_container_width=True):
                        st.session_state[f"editing_{section_id}_{idx}"] = True
                with col3:
                    if st.button("🗑️", key=f"delete_{section_id}_{idx}", help="Delete", use_container_width=True):
                        try:
                            ws.delete_rows(idx + 2)
                            st.success(f"Deleted from {section_label}.")
                            st.session_state[df_key] = pd.DataFrame(ws.get_all_records())
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting: {str(e)}")
                if st.session_state.get(f"editing_{section_id}_{idx}", False):
                    with st.expander(f"Edit: {item_name}", expanded=True):
                        edit_val = st.text_input("", value=item_name, key=f"edit_input_{section_id}_{idx}")
                        ec1, ec2 = st.columns([1, 1])
                        with ec1:
                            if st.button("☁️ Save changes", key=f"save_edit_{section_id}_{idx}"):
                                try:
                                    ws.update(values=[[edit_val]], range_name=f"A{idx+2}")
                                    st.success("Updated.")
                                    st.session_state[f"editing_{section_id}_{idx}"] = False
                                    st.session_state[df_key] = pd.DataFrame(ws.get_all_records())
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        with ec2:
                            if st.button("❌ Cancel", key=f"cancel_edit_{section_id}_{idx}"):
                                st.session_state[f"editing_{section_id}_{idx}"] = False
                                st.rerun()
            else:
                checked = st.checkbox(
                    item_name,
                    value=checklist.get(item_key, False),
                    key=f"check_{item_key}_{today_str}",
                )
                checklist[item_key] = checked

        if show_management:
            nc1, nc2, nc3 = st.columns([4, 1, 1])
            with nc1:
                new_val = st.text_input("", placeholder="Add new...", key=f"new_input_{section_id}", label_visibility="collapsed")
            with nc2:
                add_clicked = st.button("➕", key=f"add_{section_id}", help="Add", use_container_width=True)
            with nc3:
                if st.button("🗑️", key=f"clear_{section_id}", help="Clear", use_container_width=True):
                    st.session_state[f"new_input_{section_id}"] = ""
                    st.rerun()
            if add_clicked and new_val and new_val.strip():
                try:
                    ws.append_row([new_val.strip()])
                    st.success(f"Added to {section_label}.")
                    st.session_state[df_key] = pd.DataFrame(ws.get_all_records())
                    st.session_state[f"_clear_new_input_{section_id}"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding: {str(e)}")
            elif add_clicked:
                st.error("Please enter an item.")

        total = len([r for _, r in df.iterrows() if str(r.get(column_name, "")).strip()])
        checked_count = sum(1 for v in checklist.values() if v)
        progress = min(checked_count / total, 1.0) if total > 0 else 0
        st.progress(progress)
        st.caption(f"Completed: {checked_count}/{total} ({progress:.0%})")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("⚙️ Manage", key=f"manage_{section_id}", help="Edit or delete items", disabled=show_management):
                st.session_state[show_mgmt_key] = True
                st.rerun()
        with c2:
            if show_management and st.button("☁️ Done", key=f"done_{section_id}", help="Close management"):
                st.session_state[show_mgmt_key] = False
                st.rerun()
    else:
        empty_msg = "No items yet." if section_id == "other" else f"No {section_label.lower()} yet."
        st.info(f"{empty_msg} Click **Manage** to add your first item.")
        if st.button("⚙️ Manage", key=f"manage_empty_{section_id}"):
            st.session_state[show_mgmt_key] = True
            st.rerun()
        if show_management:
            nc1, nc2, nc3 = st.columns([4, 1, 1])
            with nc1:
                new_val = st.text_input("", placeholder="Add new...", key=f"new_input_empty_{section_id}", label_visibility="collapsed")
            with nc2:
                add_clicked = st.button("➕", key=f"add_empty_{section_id}", help="Add", use_container_width=True)
            with nc3:
                if st.button("🗑️", key=f"clear_empty_{section_id}", help="Clear", use_container_width=True):
                    st.session_state[f"new_input_empty_{section_id}"] = ""
                    st.rerun()
            if add_clicked and new_val and new_val.strip():
                try:
                    ws.append_row([new_val.strip()])
                    st.success(f"Added to {section_label}.")
                    st.session_state[df_key] = pd.DataFrame(ws.get_all_records())
                    st.session_state[f"_clear_new_input_empty_{section_id}"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding: {str(e)}")
            elif add_clicked:
                st.error("Please enter an item.")
            if st.button("☁️ Done", key=f"done_empty_{section_id}"):
                st.session_state[show_mgmt_key] = False
                st.rerun()


st.title("⭐ Routines")
st.caption(today.strftime("%A, %B %d, %Y"))

tab_morning, tab_evening, tab_other = st.tabs(["☀️ Morning Routine", "🌙 Evening Routine", "⭐ Other"])

with tab_morning:
    render_section(
        client,
        "morning",
        "empowering_morning_routine",
        "empowering_morning_routine",
        "Morning Routine",
        "☀️",
    )

with tab_evening:
    render_section(
        client,
        "evening",
        "empowering_evening_routine",
        "empowering_evening_routine",
        "Evening Routine",
        "🌙",
    )

with tab_other:
    render_section(
        client,
        "other",
        "daily_empowering_habits",
        "daily_empowering_habits",
        "Other",
        "⭐",
    )
