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

# Load data from all daily log sheets
def load_all_daily_data():
    """Load data from all daily log sheets"""
    data_sources = {
        "sleep": "sleep_schedule",
        "nutrition": "nutrition_and_hydration", 
        "fitness": "fitness_activities",
        "growth": "growth_and_reflection",
        "body_composition": "body_composition"
    }
    
    all_data = {}
    
    for data_type, sheet_name in data_sources.items():
        try:
            ws = client.open(sheet_name).sheet1
            df = pd.DataFrame(ws.get_all_records())
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                all_data[data_type] = df
        except Exception as e:
            st.warning(f"Could not load {data_type} data: {str(e)}")
            all_data[data_type] = pd.DataFrame()
    
    return all_data

# Initialize session state
if "daily_summary_data" not in st.session_state:
    st.session_state.daily_summary_data = load_all_daily_data()

st.title("🤖 Daily AI Summary")

# Date selector
selected_date = st.date_input(
    "Select Date for Summary", 
    value=date.today(),
    help="Choose the date you want an AI summary for"
)

# Load fresh data
if st.button("🔄 Refresh Data"):
    st.session_state.daily_summary_data = load_all_daily_data()
    st.rerun()

# Filter data for selected date
selected_data = {}
for data_type, df in st.session_state.daily_summary_data.items():
    if not df.empty and 'date' in df.columns:
        # Filter for selected date
        date_filtered = df[df['date'].dt.date == selected_date]
        selected_data[data_type] = date_filtered
    else:
        selected_data[data_type] = pd.DataFrame()

# Check if we have any data for the selected date
has_data = any(not df.empty for df in selected_data.values())

if not has_data:
    st.info(f"No data found for {selected_date.strftime('%B %d, %Y')}. Please log some activities first!")
    st.stop()

# Generate comprehensive daily summary
st.markdown("### 🎯 Daily AI Summary & Insights")

try:
    # Create comprehensive data summary for AI
    daily_summary_text = f"""
Daily Summary for {selected_date.strftime('%B %d, %Y')}:

"""
    
    # Add data from each source
    for data_type, df in selected_data.items():
        if not df.empty:
            if data_type == "sleep":
                daily_summary_text += f"""
SLEEP DATA:
"""
                for _, row in df.iterrows():
                    daily_summary_text += f"- Sleep: {row.get('sleep_start', 'N/A')} to {row.get('sleep_end', 'N/A')}\n"
            
            elif data_type == "nutrition":
                daily_summary_text += f"""
NUTRITION DATA:
"""
                for _, row in df.iterrows():
                    daily_summary_text += f"- Water: {row.get('water_ml', 0)}ml\n"
                    if row.get('breakfast'):
                        daily_summary_text += f"- Breakfast: {row.get('breakfast')}\n"
                    if row.get('lunch'):
                        daily_summary_text += f"- Lunch: {row.get('lunch')}\n"
                    if row.get('dinner'):
                        daily_summary_text += f"- Dinner: {row.get('dinner')}\n"
                    if row.get('snacks'):
                        daily_summary_text += f"- Snacks: {row.get('snacks')}\n"
            
            elif data_type == "fitness":
                daily_summary_text += f"""
FITNESS DATA:
"""
                for _, row in df.iterrows():
                    if row.get('exercise'):
                        daily_summary_text += f"- Exercise: {row.get('exercise')}\n"
                    if row.get('duration_sec'):
                        duration_min = row.get('duration_sec', 0) / 60
                        daily_summary_text += f"- Duration: {duration_min:.1f} minutes\n"
                    if row.get('distance_km'):
                        daily_summary_text += f"- Distance: {row.get('distance_km')}km\n"
            
            elif data_type == "growth":
                daily_summary_text += f"""
GROWTH & REFLECTION DATA:
"""
                for _, row in df.iterrows():
                    if row.get('mood'):
                        daily_summary_text += f"- Mood: {row.get('mood')}\n"
                    if row.get('gratitude'):
                        gratitude = str(row.get('gratitude', ''))[:200]
                        daily_summary_text += f"- Gratitude: {gratitude}\n"
                    if row.get('professional_development'):
                        daily_summary_text += f"- Professional Development: {row.get('professional_development')}\n"
                    if row.get('personal_growth'):
                        daily_summary_text += f"- Personal Growth: {row.get('personal_growth')}\n"
            
            elif data_type == "body_composition":
                daily_summary_text += f"""
BODY COMPOSITION DATA:
"""
                for _, row in df.iterrows():
                    if row.get('weight_lb'):
                        daily_summary_text += f"- Weight: {row.get('weight_lb')} lbs\n"
                    if row.get('body_fat_percent'):
                        daily_summary_text += f"- Body Fat: {row.get('body_fat_percent')}%\n"
                    if row.get('skeletal_muscle_percent'):
                        daily_summary_text += f"- Muscle: {row.get('skeletal_muscle_percent')}%\n"
    
    # Generate AI insights for the comprehensive daily summary
    insights = ai_assistant.generate_comprehensive_daily_insights(selected_data, daily_summary_text, selected_date)
    ai_assistant.display_insights(insights)
    
except Exception as e:
    st.error(f"AI Summary Error: {str(e)}")
    st.info("AI insights temporarily unavailable. Check your OpenAI API key.")

# Daily Progress Overview
st.markdown("### 📊 Daily Progress Overview")

# Create progress cards for each category
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Sleep", 
        "✅" if not selected_data["sleep"].empty else "❌",
        help="Sleep data logged"
    )

with col2:
    st.metric(
        "Nutrition", 
        "✅" if not selected_data["nutrition"].empty else "❌",
        help="Nutrition data logged"
    )

with col3:
    st.metric(
        "Fitness", 
        "✅" if not selected_data["fitness"].empty else "❌",
        help="Fitness data logged"
    )

with col4:
    st.metric(
        "Growth", 
        "✅" if not selected_data["growth"].empty else "❌",
        help="Growth data logged"
    )

with col5:
    st.metric(
        "Body Comp", 
        "✅" if not selected_data["body_composition"].empty else "❌",
        help="Body composition data logged"
    )

# Detailed data display
st.markdown("### 📋 Daily Log Details")

# Show data for each category that has entries
for data_type, df in selected_data.items():
    if not df.empty:
        with st.expander(f"📝 {data_type.replace('_', ' ').title()} Logs", expanded=True):
            # Remove date column for display since we're showing specific date
            display_df = df.drop(columns=['date'], errors='ignore')
            
            # Format specific columns for better display
            if data_type == "fitness" and 'duration_sec' in display_df.columns:
                display_df['Duration (min)'] = (display_df['duration_sec'] / 60).round(1)
                display_df = display_df.drop(columns=['duration_sec'], errors='ignore')
            
            st.dataframe(display_df, use_container_width=True)

# Weekly trend analysis
st.markdown("### 📈 Weekly Trends")

# Get data for the past 7 days
week_data = {}
for data_type, df in st.session_state.daily_summary_data.items():
    if not df.empty and 'date' in df.columns:
        week_ago = selected_date - timedelta(days=7)
        week_df = df[df['date'].dt.date >= week_ago]
        week_df = week_df[week_df['date'].dt.date <= selected_date]
        week_data[data_type] = week_df
    else:
        week_data[data_type] = pd.DataFrame()

# Create weekly activity chart
if any(not df.empty for df in week_data.values()):
    activity_data = []
    for data_type, df in week_data.items():
        if not df.empty:
            for _, row in df.iterrows():
                activity_data.append({
                    'Date': row['date'].date(),
                    'Category': data_type.replace('_', ' ').title(),
                    'Logged': True
                })
    
    if activity_data:
        activity_df = pd.DataFrame(activity_data)
        
        # Count activities per day
        daily_counts = activity_df.groupby(['Date', 'Category']).size().reset_index(name='Count')
        
        # Create stacked bar chart
        fig = px.bar(
            daily_counts, 
            x='Date', 
            y='Count', 
            color='Category',
            title="Daily Activity Logs (Past 7 Days)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Logs",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Smart suggestions for tomorrow
st.markdown("### 🎯 Suggestions for Tomorrow")

try:
    # Generate suggestions based on today's data
    suggestions = ai_assistant.get_daily_suggestions(selected_data, selected_date)
    
    for i, suggestion in enumerate(suggestions, 1):
        st.markdown(f"""
        <div style="
            background-color: #f0f8ff;
            border-left: 4px solid #1e90ff;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 4px;
            font-size: 14px;
        ">
            <strong>💡 Suggestion {i}:</strong> {suggestion}
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.info("AI suggestions temporarily unavailable.")

# Footer
st.markdown("---")
st.caption("🤖 Daily AI Summary powered by OpenAI GPT-3.5-turbo")
