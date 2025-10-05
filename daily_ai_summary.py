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
            ws.append_row(["date", "section", "insights"])
        
        ws.append_row([date.strftime('%Y-%m-%d'), section, insights])
        return True
    except:
        return False

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
            st.write(section_insights['insights'].iloc[0])
        else:
            st.info("No stored insights available for this section and date.")
    
    with col2:
        if st.button(f"Generate New", key=f"generate_{section_name}"):
            try:
                insights = ai_assistant.generate_insights(section_name.lower().replace(" & ", "_").replace(" ", "_"), {})
                ai_assistant.display_insights(insights)
                
                if save_ai_insights(selected_date, section_name, str(insights)):
                    st.success("Insights saved!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
    
    st.markdown("---")

if st.session_state.ai_insights_data.empty:
    st.markdown("### 📋 Getting Started")
    st.info("""
    **First time using AI insights?** 
    
    No setup needed! The Google Sheet will be created automatically when you generate your first insights.
    
    Just click "Generate New" for any section to get started!
    """)