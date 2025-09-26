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

creds = Credentials.from_service_account_file(
    "bewell360-credentials.json",
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("empowering_evening_routine").sheet1

# Load Data
if "evening_routine_df" not in st.session_state:
    st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())

st.title("🌙 Empowering Evening Routine")

# Entry Form
st.subheader("Add New Routine Item")
col1, col2 = st.columns([2, 1])

with col1:
    new_item = st.text_input("Routine Item", placeholder="e.g., Read for 30 minutes, Journal, Meditate")
with col2:
    priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)

col3, col4 = st.columns(2)
with col3:
    estimated_duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, value=15, step=5)
with col4:
    category = st.selectbox("Category", ["Mindfulness", "Self-Care", "Planning", "Learning", "Health", "Other"])

notes = st.text_area("Notes (optional)", placeholder="Any additional details or reminders...")

# Action Buttons
col_save, col_clear = st.columns([1, 1])
with col_save:
    add_clicked = st.button("➕ Add Item", type="primary")
with col_clear:
    clear_clicked = st.button("🗑️ Clear Form")

# Handle Add Item
if add_clicked:
    if new_item.strip():
        try:
            # Get current max order
            if not st.session_state.evening_routine_df.empty:
                max_order = st.session_state.evening_routine_df.get('order', pd.Series([0])).max()
                new_order = int(max_order) + 1 if not pd.isna(max_order) else 1
            else:
                new_order = 1
            
            # Add new item
            ws.append_row([
                str(date.today()),
                new_item.strip(),
                priority,
                estimated_duration,
                category,
                notes.strip() if notes.strip() else "",
                new_order
            ])
            st.success(f"Added '{new_item}' to your evening routine!")
            st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
            st.rerun()
        except Exception as e:
            st.error(f"Error adding item: {str(e)}")
    else:
        st.error("Please enter a routine item.")

# Handle Clear Form
if clear_clicked:
    st.rerun()

# Display Current Routine
st.subheader("Your Evening Routine")

if not st.session_state.evening_routine_df.empty:
    df = st.session_state.evening_routine_df.copy()
    
    # Convert order to numeric for proper sorting
    df['order'] = pd.to_numeric(df.get('order', 0), errors='coerce')
    df = df.sort_values('order', na_position='last')
    
    # Display routine items with controls
    for idx, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{row.get('item', 'N/A')}**")
                if row.get('notes'):
                    st.caption(f"💭 {row.get('notes')}")
                st.caption(f"⏱️ {row.get('duration', 'N/A')} min • {row.get('category', 'N/A')} • {row.get('priority', 'N/A')} priority")
            
            with col2:
                if st.button("✏️", key=f"edit_{idx}", help="Edit item"):
                    st.session_state[f"editing_{idx}"] = True
            
            with col3:
                if st.button("⬆️", key=f"up_{idx}", help="Move up"):
                    try:
                        current_order = row.get('order', 0)
                        # Find item above
                        above_items = df[df['order'] < current_order]
                        if not above_items.empty:
                            above_order = above_items['order'].max()
                            # Swap orders
                            ws.update(f"G{idx+2}", [[above_order]])
                            ws.update(f"G{above_items.index[above_items['order'] == above_order].tolist()[0]+2}", [[current_order]])
                            st.success("Moved item up!")
                            st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error moving item: {str(e)}")
            
            with col4:
                if st.button("⬇️", key=f"down_{idx}", help="Move down"):
                    try:
                        current_order = row.get('order', 0)
                        # Find item below
                        below_items = df[df['order'] > current_order]
                        if not below_items.empty:
                            below_order = below_items['order'].min()
                            # Swap orders
                            ws.update(f"G{idx+2}", [[below_order]])
                            ws.update(f"G{below_items.index[below_items['order'] == below_order].tolist()[0]+2}", [[current_order]])
                            st.success("Moved item down!")
                            st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error moving item: {str(e)}")
            
            with col5:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete item"):
                    try:
                        ws.delete_rows(idx + 2)  # +2 because of header row and 0-based index
                        st.success(f"Deleted '{row.get('item', 'item')}' from routine!")
                        st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting item: {str(e)}")
            
            # Edit form (appears when edit button is clicked)
            if st.session_state.get(f"editing_{idx}", False):
                with st.expander(f"Edit: {row.get('item', 'N/A')}", expanded=True):
                    edit_col1, edit_col2 = st.columns([2, 1])
                    
                    with edit_col1:
                        edit_item = st.text_input("Item", value=row.get('item', ''), key=f"edit_item_{idx}")
                    with edit_col2:
                        edit_priority = st.selectbox("Priority", ["High", "Medium", "Low"], 
                                                   index=["High", "Medium", "Low"].index(row.get('priority', 'Medium')), 
                                                   key=f"edit_priority_{idx}")
                    
                    edit_col3, edit_col4 = st.columns(2)
                    with edit_col3:
                        edit_duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, 
                                                       value=int(row.get('duration', 15)), step=5, key=f"edit_duration_{idx}")
                    with edit_col4:
                        edit_category = st.selectbox("Category", ["Mindfulness", "Self-Care", "Planning", "Learning", "Health", "Other"],
                                                   index=["Mindfulness", "Self-Care", "Planning", "Learning", "Health", "Other"].index(row.get('category', 'Other')), 
                                                   key=f"edit_category_{idx}")
                    
                    edit_notes = st.text_area("Notes", value=row.get('notes', ''), key=f"edit_notes_{idx}")
                    
                    edit_save_col, edit_cancel_col = st.columns([1, 1])
                    with edit_save_col:
                        if st.button("💾 Save Changes", key=f"save_edit_{idx}"):
                            try:
                                ws.update(values=[[edit_item, edit_priority, edit_duration, edit_category, edit_notes]], 
                                         range_name=f"B{idx+2}:F{idx+2}")
                                st.success("Item updated successfully!")
                                st.session_state[f"editing_{idx}"] = False
                                st.session_state.evening_routine_df = pd.DataFrame(ws.get_all_records())
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating item: {str(e)}")
                    
                    with edit_cancel_col:
                        if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()
            
            st.divider()

    # Analytics
    st.subheader("Routine Analytics")
    
    if len(df) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_items = len(df)
            st.metric("Total Items", total_items)
        
        with col2:
            total_duration = df['duration'].sum() if 'duration' in df.columns else 0
            st.metric("Total Duration", f"{total_duration} min")
        
        with col3:
            high_priority = len(df[df.get('priority') == 'High']) if 'priority' in df.columns else 0
            st.metric("High Priority", high_priority)
        
        with col4:
            categories = df['category'].nunique() if 'category' in df.columns else 0
            st.metric("Categories", categories)
        
        # Category breakdown
        if 'category' in df.columns and not df['category'].isna().all():
            st.subheader("Routine by Category")
            category_counts = df['category'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index, 
                        title="Routine Items by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        # Priority breakdown
        if 'priority' in df.columns and not df['priority'].isna().all():
            st.subheader("Routine by Priority")
            priority_counts = df['priority'].value_counts()
            fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                        title="Routine Items by Priority",
                        labels={'x': 'Priority', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No evening routine items yet. Add your first item above to get started!")
    st.markdown("""
    ### 💡 Evening Routine Ideas:
    - **Mindfulness**: Meditation, deep breathing, gratitude journaling
    - **Self-Care**: Skincare routine, reading, relaxing music
    - **Planning**: Review tomorrow's schedule, set intentions
    - **Learning**: Read educational content, listen to podcasts
    - **Health**: Stretching, light exercise, prepare healthy snacks
    """)