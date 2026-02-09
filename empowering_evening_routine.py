import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("empowering_evening_routine").sheet1

if "evening_routine_df" not in st.session_state:
    st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())

today = date.today()
today_str = today.strftime("%Y-%m-%d")

if f"daily_checklist_{today_str}" not in st.session_state:
    st.session_state[f"daily_checklist_{today_str}"] = {}

if st.session_state.pop("_clear_new_routine_input", None):
    st.session_state["new_routine_input"] = ""
if st.session_state.pop("_clear_new_routine_input_empty", None):
    st.session_state["new_routine_input_empty"] = ""

st.title("🌙 Empowering Evening Routine")

st.subheader(today.strftime('%B %d, %Y'))

if not st.session_state.evening_routine_df.empty:
    df = st.session_state.evening_routine_df.copy()
    
    for idx, row in df.iterrows():
        routine_key = f"routine_{idx}"
        routine_name = str(row.get('empowering_evening_routine', '')).strip()
        
        if routine_name == '':
            continue
        
        if st.session_state.get("show_management", False):
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                checked = st.checkbox(
                    routine_name,
                    value=st.session_state[f"daily_checklist_{today_str}"].get(routine_key, False),
                    key=f"check_{routine_key}_{today_str}"
                )
                st.session_state[f"daily_checklist_{today_str}"][routine_key] = checked
            
            with col2:
                if st.button("✏️", key=f"edit_{idx}", help="Edit", use_container_width=True):
                    st.session_state[f"editing_{idx}"] = True
            
            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete", use_container_width=True):
                    try:
                        ws.delete_rows(idx + 2)
                        st.success(f"Deleted '{routine_name}' from routines!")
                        st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting routine: {str(e)}")
            
            if st.session_state.get(f"editing_{idx}", False):
                with st.expander(f"Edit: {routine_name}", expanded=True):
                    edit_routine = st.text_input("Routine", value=routine_name, key=f"edit_routine_{idx}")
                    
                    edit_save_col, edit_cancel_col = st.columns([1, 1])
                    with edit_save_col:
                        if st.button("☁️ Save Changes", key=f"save_edit_{idx}"):
                            try:
                                ws.update(values=[[edit_routine]], 
                                         range_name=f"A{idx+2}")
                                st.success("Routine updated successfully!")
                                st.session_state[f"editing_{idx}"] = False
                                st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating routine: {str(e)}")
                    
                    with edit_cancel_col:
                        if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()
        else:
            checked = st.checkbox(
                routine_name,
                value=st.session_state[f"daily_checklist_{today_str}"].get(routine_key, False),
                key=f"check_{routine_key}_{today_str}"
            )
            st.session_state[f"daily_checklist_{today_str}"][routine_key] = checked
    
    if st.session_state.get("show_management", False):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            new_routine = st.text_input("", placeholder="Add new routine...", key="new_routine_input", label_visibility="collapsed")
        
        with col2:
            add_clicked = st.button("➕", key="add_new_routine", help="Add routine", use_container_width=True)
        
        with col3:
            if st.button("🗑️", key="clear_new_routine", help="Clear", use_container_width=True):
                st.session_state["new_routine_input"] = ""
                st.rerun()
        
        if add_clicked:
            if new_routine.strip():
                try:
                    ws.append_row([new_routine.strip()])
                    st.success(f"Added '{new_routine}' to your evening routines!")
                    st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                    st.session_state["_clear_new_routine_input"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding routine: {str(e)}")
            else:
                st.error("Please enter a routine.")
    
    total_items = len([row for _, row in df.iterrows() if str(row.get('empowering_evening_routine', '')).strip()])
    checked_items = sum(st.session_state[f"daily_checklist_{today_str}"].values())
    progress = min(checked_items / total_items, 1.0) if total_items > 0 else 0
    
    st.progress(progress)
    st.caption(f"Completed: {checked_items}/{total_items} items ({progress:.0%})")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⚙️ Manage Routines", help="Edit or delete routine items", disabled=st.session_state.get("show_management", False)):
            st.session_state["show_management"] = True
            st.rerun()
    
    with col2:
        if st.session_state.get("show_management", False):
            if st.button("☁️ Save", help="Close management section"):
                st.session_state["show_management"] = False
                st.rerun()

else:
    st.info("No evening routines yet. Click 'Manage Routines' below to add your first routine!")
    
    if st.button("⚙️ Manage Routines", help="Add your first routine"):
        st.session_state["show_management"] = True
        st.rerun()
    
    if st.session_state.get("show_management", False):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            new_routine = st.text_input("", placeholder="Add new routine...", key="new_routine_input_empty", label_visibility="collapsed")
        
        with col2:
            add_clicked = st.button("➕", key="add_new_routine_empty", help="Add routine", use_container_width=True)
        
        with col3:
            if st.button("🗑️", key="clear_new_routine_empty", help="Clear", use_container_width=True):
                st.session_state["new_routine_input_empty"] = ""
                st.rerun()
        
        if add_clicked:
            if new_routine.strip():
                try:
                    ws.append_row([new_routine.strip()])
                    st.success(f"Added '{new_routine}' to your evening routines!")
                    st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                    st.session_state["_clear_new_routine_input_empty"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding routine: {str(e)}")
            else:
                st.error("Please enter a routine.")
        
        if st.button("☁️ Save", help="Close management section"):
            st.session_state["show_management"] = False
            st.rerun()
