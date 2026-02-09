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
ws = client.open("daily_empowering_habits").sheet1

if "daily_habits_df" not in st.session_state:
    st.session_state.daily_habits_df = pd.DataFrame(ws.get_all_records())

today = date.today()
today_str = today.strftime("%Y-%m-%d")

if f"daily_checklist_{today_str}" not in st.session_state:
    st.session_state[f"daily_checklist_{today_str}"] = {}

if st.session_state.pop("_clear_new_habit_input", None):
    st.session_state["new_habit_input"] = ""
if st.session_state.pop("_clear_new_habit_input_empty", None):
    st.session_state["new_habit_input_empty"] = ""

st.title("⭐ Daily Empowering Habits")

st.subheader(today.strftime('%B %d, %Y'))

if not st.session_state.daily_habits_df.empty:
    df = st.session_state.daily_habits_df.copy()
    
    for idx, row in df.iterrows():
        habit_key = f"habit_{idx}"
        habit_name = str(row.get('daily_empowering_habits', '')).strip()
        
        if habit_name == '':
            continue
        
        if st.session_state.get("show_management", False):
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                checked = st.checkbox(
                    habit_name,
                    value=st.session_state[f"daily_checklist_{today_str}"].get(habit_key, False),
                    key=f"check_{habit_key}_{today_str}"
                )
                st.session_state[f"daily_checklist_{today_str}"][habit_key] = checked
            
            with col2:
                if st.button("✏️", key=f"edit_{idx}", help="Edit", use_container_width=True):
                    st.session_state[f"editing_{idx}"] = True
            
            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete", use_container_width=True):
                    try:
                        ws.delete_rows(idx + 2)
                        st.success(f"Deleted '{habit_name}' from habits!")
                        st.session_state.daily_habits_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting habit: {str(e)}")
            
            if st.session_state.get(f"editing_{idx}", False):
                with st.expander(f"Edit: {habit_name}", expanded=True):
                    edit_habit = st.text_input("Habit", value=habit_name, key=f"edit_habit_{idx}")
                    
                    edit_save_col, edit_cancel_col = st.columns([1, 1])
                    with edit_save_col:
                        if st.button("☁️ Save Changes", key=f"save_edit_{idx}"):
                            try:
                                ws.update(values=[[edit_habit]], 
                                         range_name=f"A{idx+2}")
                                st.success("Habit updated successfully!")
                                st.session_state[f"editing_{idx}"] = False
                                st.session_state.daily_habits_df = pd.DataFrame(ws.get_all_records())
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating habit: {str(e)}")
                    
                    with edit_cancel_col:
                        if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()
        else:
            checked = st.checkbox(
                habit_name,
                value=st.session_state[f"daily_checklist_{today_str}"].get(habit_key, False),
                key=f"check_{habit_key}_{today_str}"
            )
            st.session_state[f"daily_checklist_{today_str}"][habit_key] = checked
    
    if st.session_state.get("show_management", False):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            new_habit = st.text_input("", placeholder="Add new habit...", key="new_habit_input", label_visibility="collapsed")
        
        with col2:
            add_clicked = st.button("➕", key="add_new_habit", help="Add habit", use_container_width=True)
        
        with col3:
            if st.button("🗑️", key="clear_new_habit", help="Clear", use_container_width=True):
                st.session_state["new_habit_input"] = ""
                st.rerun()
        
        if add_clicked:
            if new_habit.strip():
                try:
                    ws.append_row([new_habit.strip()])
                    st.success(f"Added '{new_habit}' to your daily habits!")
                    st.session_state.daily_habits_df = pd.DataFrame(ws.get_all_records())
                    st.session_state["_clear_new_habit_input"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding habit: {str(e)}")
            else:
                st.error("Please enter a habit.")
    
    total_items = len([row for _, row in df.iterrows() if str(row.get('daily_empowering_habits', '')).strip()])
    checked_items = sum(st.session_state[f"daily_checklist_{today_str}"].values())
    progress = min(checked_items / total_items, 1.0) if total_items > 0 else 0
    
    st.progress(progress)
    st.caption(f"Completed: {checked_items}/{total_items} items ({progress:.0%})")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⚙️ Manage Habits", help="Edit or delete habit items", disabled=st.session_state.get("show_management", False)):
            st.session_state["show_management"] = True
            st.rerun()
    
    with col2:
        if st.session_state.get("show_management", False):
            if st.button("☁️ Save", help="Close management section"):
                st.session_state["show_management"] = False
                st.rerun()

else:
    st.info("No daily habits yet. Click 'Manage Habits' below to add your first habit!")
    
    if st.button("⚙️ Manage Habits", help="Add your first habit"):
        st.session_state["show_management"] = True
        st.rerun()
    
    if st.session_state.get("show_management", False):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            new_habit = st.text_input("", placeholder="Add new habit...", key="new_habit_input_empty", label_visibility="collapsed")
        
        with col2:
            add_clicked = st.button("➕", key="add_new_habit_empty", help="Add habit", use_container_width=True)
        
        with col3:
            if st.button("🗑️", key="clear_new_habit_empty", help="Clear", use_container_width=True):
                st.session_state["new_habit_input_empty"] = ""
                st.rerun()
        
        if add_clicked:
            if new_habit.strip():
                try:
                    ws.append_row([new_habit.strip()])
                    st.success(f"Added '{new_habit}' to your daily habits!")
                    st.session_state.daily_habits_df = pd.DataFrame(ws.get_all_records())
                    st.session_state["_clear_new_habit_input_empty"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding habit: {str(e)}")
            else:
                st.error("Please enter a habit.")
        
        if st.button("☁️ Save", help="Close management section"):
            st.session_state["show_management"] = False
            st.rerun()
