import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime
import plotly.express as px

# Google Sheets Setup
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

# Load Data
if "evening_routine_df" not in st.session_state:
    st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())

# Get today's date for daily reset
today = date.today()
today_str = today.strftime("%Y-%m-%d")

# Initialize daily checklist state
if f"daily_checklist_{today_str}" not in st.session_state:
    st.session_state[f"daily_checklist_{today_str}"] = {}

st.title("🌙 Empowering Evening Routine")

# Daily Checklist
st.subheader(f"Today's Evening Routine - {today.strftime('%B %d, %Y')}")

if not st.session_state.evening_routine_df.empty:
    df = st.session_state.evening_routine_df.copy()
    
    # Display checklist items
    for idx, row in df.iterrows():
        routine_key = f"routine_{idx}"
        routine_name = row.get('routine', 'N/A')
        
        # Create checkbox for each routine
        checked = st.checkbox(
            routine_name,
            value=st.session_state[f"daily_checklist_{today_str}"].get(routine_key, False),
            key=f"check_{routine_key}_{today_str}"
        )
        
        # Update the daily checklist state
        st.session_state[f"daily_checklist_{today_str}"][routine_key] = checked
    
    # Show progress
    total_items = len(df)
    checked_items = sum(st.session_state[f"daily_checklist_{today_str}"].values())
    progress = checked_items / total_items if total_items > 0 else 0
    
    st.progress(progress)
    st.caption(f"Completed: {checked_items}/{total_items} items ({progress:.0%})")
    
    st.divider()
    
    # Management section
    st.subheader("Manage Routine Items")
    
    # Display routine items with controls
    for idx, row in df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{row.get('routine', 'N/A')}**")
            
            with col2:
                if st.button("✏️", key=f"edit_{idx}", help="Edit item"):
                    st.session_state[f"editing_{idx}"] = True
            
            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete routine"):
                    try:
                        ws.delete_rows(idx + 2)  # +2 because of header row and 0-based index
                        st.success(f"Deleted '{row.get('routine', 'routine')}' from routine!")
                        st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting routine: {str(e)}")
            
            # Edit form (appears when edit button is clicked)
            if st.session_state.get(f"editing_{idx}", False):
                with st.expander(f"Edit: {row.get('routine', 'N/A')}", expanded=True):
                    edit_routine = st.text_input("Routine", value=row.get('routine', ''), key=f"edit_routine_{idx}")
                    
                    edit_save_col, edit_cancel_col = st.columns([1, 1])
                    with edit_save_col:
                        if st.button("💾 Save Changes", key=f"save_edit_{idx}"):
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
            
            st.divider()

    # Analytics
    st.subheader("Routine Analytics")
    
    if len(df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            total_routines = len(df)
            st.metric("Total Routines", total_routines)
        
        with col2:
            checked_routines = sum(st.session_state[f"daily_checklist_{today_str}"].values())
            st.metric("Completed Today", f"{checked_routines}/{total_routines}")

else:
    st.info("No evening routines yet. Add your first routine below to get started!")

# Add New Routine Section (at the end)
st.subheader("Add New Routine Item")
new_routine = st.text_input("Routine", placeholder="e.g., Read, Journal, Meditate, Prepare tomorrow's clothes")

# Action Buttons
col_save, col_clear = st.columns([1, 1])
with col_save:
    add_clicked = st.button("➕ Add Item", type="primary")
with col_clear:
    clear_clicked = st.button("🗑️ Clear Form")

# Handle Add Item
if add_clicked:
    if new_routine.strip():
        try:
            # Add new routine
            ws.append_row([
                new_routine.strip()
            ])
            st.success(f"Added '{new_routine}' to your evening routine!")
            st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
            st.rerun()
        except Exception as e:
            st.error(f"Error adding routine: {str(e)}")
    else:
        st.error("Please enter a routine.")

# Handle Clear Form
if clear_clicked:
    st.rerun()
