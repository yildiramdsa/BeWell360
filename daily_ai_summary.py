import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from ai_assistant_api import ai_assistant
import plotly.express as px
import plotly.graph_objects as go

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

# Load AI insights from storage
def load_ai_insights():
    """Load stored AI insights from spreadsheet"""
    try:
        ws = client.open("daily_ai_insights").sheet1
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except gspread.SpreadsheetNotFound:
        # Sheet doesn't exist yet - this is normal for first-time users
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Could not load AI insights: {str(e)}")
        return pd.DataFrame()

def save_ai_insights(date, section, insights):
    """Save AI insights to spreadsheet"""
    try:
        # Try to open existing sheet
        try:
            ws = client.open("daily_ai_insights").sheet1
        except gspread.SpreadsheetNotFound:
            # Create new sheet if it doesn't exist
            sh = client.create("daily_ai_insights")
            ws = sh.sheet1
            # Add headers
            ws.append_row(["date", "section", "insights"])
        
        ws.append_row([date.strftime('%Y-%m-%d'), section, insights])
        return True
    except Exception as e:
        st.error(f"Could not save AI insights: {str(e)}")
        return False

# Initialize session state
if "ai_insights_data" not in st.session_state:
    st.session_state.ai_insights_data = load_ai_insights()

st.title("🦉 Daily AI Summary")

# Date selector
selected_date = st.date_input(
    "Select Date for Summary", 
    value=date.today(),
    help="Choose the date you want an AI summary for"
)

# Refresh data
if st.button("🔄 Refresh Insights"):
    st.session_state.ai_insights_data = load_ai_insights()
    st.rerun()

# Define the 4 sections
sections = {
    "🍎": "Nutrition & Hydration",
    "⚽": "Fitness Activities", 
    "🧸": "Sleep Schedule",
    "🌱": "Growth & Reflection"
}

# Filter stored insights for selected date
date_str = selected_date.strftime('%Y-%m-%d')
stored_insights = st.session_state.ai_insights_data[
    st.session_state.ai_insights_data['date'].dt.date == selected_date
] if not st.session_state.ai_insights_data.empty else pd.DataFrame()

# Display AI insights for each section
for icon, section_name in sections.items():
    st.markdown(f"### {icon} {section_name}")
    
    # Check if insights exist for this section and date
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
                # Generate new insights for this section
                insights = ai_assistant.generate_insights(section_name.lower().replace(" & ", "_").replace(" ", "_"), {})
                ai_assistant.display_insights(insights)
                
                # Save the insights
                if save_ai_insights(selected_date, section_name, str(insights)):
                    st.success("Insights saved!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
    
    st.markdown("---")

# Instructions for creating the Google Sheet
if st.session_state.ai_insights_data.empty:
    st.markdown("### 📋 Getting Started")
    st.info("""
    **First time using AI insights?** 
    
    No setup needed! The Google Sheet will be created automatically when you generate your first insights.
    
    The sheet will include these columns:
    - **date** (format: YYYY-MM-DD)
    - **section** (Nutrition & Hydration, Fitness Activities, Sleep Schedule, Growth & Reflection)  
    - **insights** (the AI-generated insights text)
    
    Just click "Generate New" for any section to get started!
    """)