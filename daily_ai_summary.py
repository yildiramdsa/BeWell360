import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from ai_assistant_api import ai_assistant

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)

def load_ai_insights():
    try:
        ws = client.open("daily_ai_insights").sheet1
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except:
        return pd.DataFrame()

def save_ai_insights(date, section, insights):
    try:
        try:
            ws = client.open("daily_ai_insights").sheet1
        except gspread.SpreadsheetNotFound:
            sh = client.create("daily_ai_insights")
            ws = sh.sheet1
            ws.append_row(["date", "section", "ai_insights"])
        
        ws.append_row([date.strftime('%Y-%m-%d'), section, insights])
        return True
    except:
        return False

def get_user_data_for_date(selected_date):
    """Load actual user data for the selected date from all sheets"""
    user_data = {}
    
    sheets_data = {
        "nutrition": "nutrition_and_hydration",
        "fitness": "fitness_activities", 
        "sleep": "sleep_schedule",
        "growth": "mood_and_gratitude",
        "body_composition": "body_composition"
    }
    
    for data_type, sheet_name in sheets_data.items():
        try:
            ws = client.open(sheet_name).sheet1
            df = pd.DataFrame(ws.get_all_records())
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                date_filtered = df[df['date'].dt.date == selected_date]
                user_data[data_type] = date_filtered
            else:
                user_data[data_type] = pd.DataFrame()
        except:
            user_data[data_type] = pd.DataFrame()
    
    return user_data

if "ai_insights_data" not in st.session_state:
    st.session_state.ai_insights_data = load_ai_insights()

st.title("🦉 Daily AI Summary")

selected_date = st.date_input(
    "Select Date for Summary", 
    value=date.today(),
    help="Choose the date you want an AI summary for"
)

if st.button("🔄 Refresh Insights"):
    st.session_state.ai_insights_data = load_ai_insights()
    st.rerun()

sections = {
    "🍎": "Nutrition & Hydration",
    "⚽": "Fitness Activities", 
    "🧸": "Sleep Schedule",
    "🌱": "Growth & Reflection"
}

user_data = get_user_data_for_date(selected_date)

has_data = any(not df.empty for df in user_data.values())
if not has_data:
    st.info(f"No data logged for {selected_date.strftime('%B %d, %Y')}. Please log some activities first!")
    st.stop()

st.markdown("### 📊 Data Available for Analysis")
data_cols = st.columns(5)
data_types = ["nutrition", "fitness", "sleep", "growth", "body_composition"]
data_icons = ["🍎", "⚽", "🧸", "🌱", "💪"]

for i, (data_type, icon) in enumerate(zip(data_types, data_icons)):
    with data_cols[i]:
        has_data_for_type = not user_data[data_type].empty
        st.metric(
            icon,
            "✅" if has_data_for_type else "❌",
            help=f"{data_type.title()} data logged" if has_data_for_type else f"No {data_type} data"
        )

date_str = selected_date.strftime('%Y-%m-%d')
stored_insights = st.session_state.ai_insights_data[
    st.session_state.ai_insights_data['date'].dt.date == selected_date
] if not st.session_state.ai_insights_data.empty else pd.DataFrame()

for icon, section_name in sections.items():
    st.markdown(f"### {icon} {section_name}")
    
    section_insights = stored_insights[stored_insights['section'] == section_name] if not stored_insights.empty else pd.DataFrame()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not section_insights.empty:
            st.markdown("**Stored Insights:**")
            st.write(section_insights['ai_insights'].iloc[0])
        else:
            st.info("No stored insights available for this section and date.")
    
    with col2:
        if st.button(f"Generate New", key=f"generate_{section_name}"):
            try:
                if section_name == "Nutrition & Hydration":
                    insights = ai_assistant.generate_ai_insights("nutrition", user_data.get("nutrition", pd.DataFrame()))
                elif section_name == "Fitness Activities":
                    insights = ai_assistant.generate_ai_insights("fitness", user_data.get("fitness", pd.DataFrame()))
                elif section_name == "Sleep Schedule":
                    insights = ai_assistant.generate_ai_insights("sleep", user_data.get("sleep", pd.DataFrame()))
                elif section_name == "Growth & Reflection":
                    insights = ai_assistant.generate_ai_insights("growth", user_data.get("growth", pd.DataFrame()))
                else:
                    insights = ai_assistant.generate_ai_insights("daily_summary", user_data)
                
                ai_assistant.display_ai_insights(insights)
                
                if save_ai_insights(selected_date, section_name, str(insights)):
                    st.success("Insights saved!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")