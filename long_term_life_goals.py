import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("long_term_life_goals").sheet1

if "life_goals_df" not in st.session_state:
    st.session_state.life_goals_df = pd.DataFrame(ws.get_all_records())

if "life_goals_completed" not in st.session_state:
    st.session_state.life_goals_completed = {}

st.title("📌 Long-Term Life Goals")

if not st.session_state.life_goals_df.empty:
    df = st.session_state.life_goals_df.copy()
    
    goal_col = None
    for col in df.columns:
        if col.lower() in ['goal', 'goals']:
            goal_col = col
            break
    
    if goal_col is None and len(df.columns) > 0:
        goal_col = df.columns[0]
    
    if goal_col is None:
        st.error("No data found in the Google Sheet. Please add some goals.")
    else:
        for idx, row in df.iterrows():
            goal_key = f"goal_{idx}"
            goal_name = str(row.get(goal_col, '')).strip()
            
            if goal_name == '':
                continue
            
            if st.session_state.get("show_management", False):
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    checked = st.checkbox(
                        goal_name,
                        value=st.session_state.life_goals_completed.get(goal_key, False),
                        key=f"check_{goal_key}"
                    )
                    st.session_state.life_goals_completed[goal_key] = checked
                
                with col2:
                    if st.button("✏️", key=f"edit_{idx}", help="Edit", use_container_width=True):
                        st.session_state[f"editing_{idx}"] = True
                
                with col3:
                    if st.button("🗑️", key=f"delete_{idx}", help="Delete", use_container_width=True):
                        try:
                            ws.delete_rows(idx + 2)
                            st.success(f"Deleted '{goal_name}' from goals!")
                            st.session_state.life_goals_df = pd.DataFrame(ws.get_all_records())
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting goal: {str(e)}")
                
                if st.session_state.get(f"editing_{idx}", False):
                    with st.expander(f"Edit: {goal_name}", expanded=True):
                        edit_goal = st.text_input("Goal", value=goal_name, key=f"edit_goal_{idx}")
                        
                        edit_save_col, edit_cancel_col = st.columns([1, 1])
                        with edit_save_col:
                            if st.button("☁️ Save Changes", key=f"save_edit_{idx}"):
                                try:
                                    ws.update(values=[[edit_goal]], 
                                             range_name=f"A{idx+2}")
                                    st.success("Goal updated successfully!")
                                    st.session_state[f"editing_{idx}"] = False
                                    st.session_state.life_goals_df = pd.DataFrame(ws.get_all_records())
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating goal: {str(e)}")
                        
                        with edit_cancel_col:
                            if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                                st.session_state[f"editing_{idx}"] = False
                                st.rerun()
            else:
                checked = st.checkbox(
                    goal_name,
                    value=st.session_state.life_goals_completed.get(goal_key, False),
                    key=f"check_{goal_key}"
                )
                st.session_state.life_goals_completed[goal_key] = checked
        
        if st.session_state.get("show_management", False):
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                new_goal = st.text_input("", placeholder="Add new goal...", key="new_goal_input", label_visibility="collapsed")
            
            with col2:
                add_clicked = st.button("➕", key="add_new_goal", help="Add goal", use_container_width=True)
            
            with col3:
                if st.button("🗑️", key="clear_new_goal", help="Clear", use_container_width=True):
                    st.session_state["new_goal_input"] = ""
                    st.rerun()
            
            if add_clicked:
                if new_goal.strip():
                    try:
                        ws.append_row([new_goal.strip()])
                        st.success(f"Added '{new_goal}' to your life goals!")
                        st.session_state.life_goals_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding goal: {str(e)}")
                else:
                    st.error("Please enter a goal.")
        
        total_items = len([row for _, row in df.iterrows() if str(row.get(goal_col, '')).strip()])
        checked_items = sum(st.session_state.life_goals_completed.values())
        progress = checked_items / total_items if total_items > 0 else 0
        
        st.progress(progress)
        st.caption(f"Completed: {checked_items}/{total_items} goals ({progress:.0%})")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("⚙️ Manage Goals", help="Edit or delete goal items", disabled=st.session_state.get("show_management", False)):
                st.session_state["show_management"] = True
                st.rerun()
        
        with col2:
            if st.session_state.get("show_management", False):
                if st.button("☁️ Save", help="Close management section"):
                    st.session_state["show_management"] = False
                    st.rerun()

else:
    st.info("No life goals yet. Click 'Manage Goals' below to add your first goal!")
    
    if st.button("⚙️ Manage Goals", help="Add your first goal"):
        st.session_state["show_management"] = True
        st.rerun()
    
    if st.session_state.get("show_management", False):
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            new_goal = st.text_input("", placeholder="Add new goal...", key="new_goal_input_empty", label_visibility="collapsed")
        
        with col2:
            add_clicked = st.button("➕", key="add_new_goal_empty", help="Add goal", use_container_width=True)
        
        with col3:
            if st.button("🗑️", key="clear_new_goal_empty", help="Clear", use_container_width=True):
                st.session_state["new_goal_input_empty"] = ""
                st.rerun()
        
        if add_clicked:
            if new_goal.strip():
                try:
                    ws.append_row([new_goal.strip()])
                    st.success(f"Added '{new_goal}' to your life goals!")
                    st.session_state.life_goals_df = pd.DataFrame(ws.get_all_records())
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding goal: {str(e)}")
            else:
                st.error("Please enter a goal.")
        
        if st.button("☁️ Save", help="Close management section"):
            st.session_state["show_management"] = False
            st.rerun()