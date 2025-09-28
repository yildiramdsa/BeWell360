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
ws = client.open("goals_for_the_year").sheet1

CATEGORIES = [
    "Health & Vitality",
    "Fun, Free Time & Family", 
    "Relationships",
    "Career & Business",
    "Financial",
    "Personal Growth & Learning",
    "Spiritual & Emotional Well-Being",
    "Lifestyle & Environment"
]

if "yearly_goals_df" not in st.session_state:
    st.session_state.yearly_goals_df = pd.DataFrame(ws.get_all_records(expected_headers=["category", "goal", "by_when", "why_i_want_it"]))

if "yearly_goals_completed" not in st.session_state:
    st.session_state.yearly_goals_completed = {}

st.title("🎯 Goals for the Year")

if not st.session_state.yearly_goals_df.empty:
    df = st.session_state.yearly_goals_df.copy()
    
    category_col = None
    goal_col = None
    deadline_col = None
    why_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['category']:
            category_col = col
        elif col_lower in ['goal']:
            goal_col = col
        elif col_lower in ['by_when', 'by when']:
            deadline_col = col
        elif col_lower in ['why_i_want_it', 'why i want it']:
            why_col = col
    
    if category_col is None and len(df.columns) > 0:
        category_col = df.columns[0] if len(df.columns) > 0 else None
    if goal_col is None and len(df.columns) > 1:
        goal_col = df.columns[1] if len(df.columns) > 1 else None
    if deadline_col is None and len(df.columns) > 2:
        deadline_col = df.columns[2] if len(df.columns) > 2 else None
    if why_col is None and len(df.columns) > 3:
        why_col = df.columns[3] if len(df.columns) > 3 else None
    
    if goal_col is None:
        st.error("No data found in the Google Sheet. Please add some goals.")
    else:
        for idx, row in df.iterrows():
            goal_key = f"goal_{idx}"
            goal_name = str(row.get(goal_col, '')).strip()
            category = str(row.get(category_col, '')).strip() if category_col else ""
            deadline = str(row.get(deadline_col, '')).strip() if deadline_col else ""
            why = str(row.get(why_col, '')).strip() if why_col else ""
            
            if goal_name == '':
                continue
            
            # Compact display
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{goal_name}**")
                info_parts = []
                if category:
                    info_parts.append(f"📂 {category}")
                if deadline:
                    info_parts.append(f"📅 {deadline}")
                if info_parts:
                    st.caption(" | ".join(info_parts))
                if why:
                    st.caption(f"💭 {why}")
            
            with col2:
                if st.session_state.get("show_management", False):
                    col_edit, col_delete = st.columns([1, 1])
                    with col_edit:
                        if st.button("✏️", key=f"edit_{idx}", help="Edit", width='stretch'):
                            st.session_state[f"editing_{idx}"] = True
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{idx}", help="Delete", width='stretch'):
                            try:
                                ws.delete_rows(idx + 2)
                                st.success("Goal deleted successfully!")
                                st.session_state.yearly_goals_df = pd.DataFrame(ws.get_all_records(expected_headers=["category", "goal", "by_when", "why_i_want_it"]))
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting goal: {str(e)}")
                else:
                    checked = st.checkbox(
                        "✓",
                        value=st.session_state.yearly_goals_completed.get(goal_key, False),
                        key=f"check_{goal_key}",
                        help="Mark as completed"
                    )
                    st.session_state.yearly_goals_completed[goal_key] = checked
            
            if st.session_state.get(f"editing_{idx}", False):
                with st.expander(f"Edit: {goal_name}", expanded=True):
                    edit_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(category) if category in CATEGORIES else 0, key=f"edit_category_{idx}")
                    edit_goal = st.text_input("What I Want (Specific Goal)", value=goal_name, key=f"edit_goal_{idx}")
                    edit_deadline = st.text_input("By When", value=deadline, key=f"edit_deadline_{idx}")
                    edit_why = st.text_area("Why I Want It", value=why, key=f"edit_why_{idx}")
                    
                    edit_save_col, edit_cancel_col = st.columns([1, 1])
                    with edit_save_col:
                        if st.button("☁️ Save Changes", key=f"save_edit_{idx}"):
                            try:
                                ws.update(values=[[edit_category, edit_goal, edit_deadline, edit_why]], 
                                         range_name=f"A{idx+2}:D{idx+2}")
                                st.success("Goal updated successfully!")
                                st.session_state[f"editing_{idx}"] = False
                                st.session_state.yearly_goals_df = pd.DataFrame(ws.get_all_records(expected_headers=["category", "goal", "by_when", "why_i_want_it"]))
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating goal: {str(e)}")
                    
                    with edit_cancel_col:
                        if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()
        
        if st.session_state.get("show_management", False):
            st.subheader("Add New Goal")
            
            new_category = st.selectbox("Category", CATEGORIES, key="new_category_input")
            new_goal = st.text_input("What I Want (Specific Goal)", key="new_goal_input")
            new_deadline = st.text_input("By When", key="new_deadline_input")
            new_why = st.text_area("Why I Want It", key="new_why_input")
            
            if new_goal.strip():
                st.session_state["pending_goal"] = [new_category, new_goal.strip(), new_deadline.strip(), new_why.strip()]
        
        total_items = len([row for _, row in df.iterrows() if str(row.get(goal_col, '')).strip()])
        checked_items = sum(st.session_state.yearly_goals_completed.values())
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
                if st.button("☁️ Save", help="Save and close management section"):
                    if st.session_state.get("pending_goal"):
                        try:
                            ws.append_row(st.session_state["pending_goal"])
                            st.success(f"Added '{st.session_state['pending_goal'][1]}' to your yearly goals!")
                            st.session_state.yearly_goals_df = pd.DataFrame(ws.get_all_records(expected_headers=["category", "goal", "by_when", "why_i_want_it"]))
                            st.session_state["pending_goal"] = []
                        except Exception as e:
                            st.error(f"Error adding goal: {str(e)}")
                    
                    # Close all edit modes
                    for key in list(st.session_state.keys()):
                        if key.startswith("editing_"):
                            st.session_state[key] = False
                    
                    # Clear form inputs by clearing pending goal
                    st.session_state["pending_goal"] = []
                    
                    st.session_state["show_management"] = False
                    st.rerun()

else:
    st.info("No yearly goals yet. Click 'Manage Goals' below to add your first goal!")
    
    if st.button("⚙️ Manage Goals", help="Add your first goal"):
        st.session_state["show_management"] = True
        st.rerun()
    
    if st.session_state.get("show_management", False):
        st.subheader("Add New Goal")
        
        new_category = st.selectbox("Category", CATEGORIES, key="new_category_input_empty")
        new_goal = st.text_input("What I Want (Specific Goal)", key="new_goal_input_empty")
        new_deadline = st.text_input("By When", key="new_deadline_input_empty")
        new_why = st.text_area("Why I Want It", key="new_why_input_empty")
        
        if new_goal.strip():
            st.session_state["pending_goal"] = [new_category, new_goal.strip(), new_deadline.strip(), new_why.strip()]
        
        if st.button("☁️ Save", help="Save and close management section"):
            if st.session_state.get("pending_goal"):
                try:
                    ws.append_row(st.session_state["pending_goal"])
                    st.success(f"Added '{st.session_state['pending_goal'][1]}' to your yearly goals!")
                    st.session_state.yearly_goals_df = pd.DataFrame(ws.get_all_records(expected_headers=["category", "goal", "by_when", "why_i_want_it"]))
                    st.session_state["pending_goal"] = []
                except Exception as e:
                    st.error(f"Error adding goal: {str(e)}")
            
            # Close all edit modes
            for key in list(st.session_state.keys()):
                if key.startswith("editing_"):
                    st.session_state[key] = False
            
            # Clear form inputs by clearing pending goal
            st.session_state["pending_goal"] = []
            
            st.session_state["show_management"] = False
            st.rerun()