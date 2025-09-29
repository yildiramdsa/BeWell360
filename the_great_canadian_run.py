import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import gspread
from google.oauth2.service_account import Credentials

# ---------------- Configuration ----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("the_great_canadian_run").sheet1

# Challenge tiers configuration
CHALLENGE_TIERS = {
    "Tier 1 - The Atlantic Challenge": {
        "total_km": 500,
        "route": "St. John's → Port aux Basques",
        "description": "Perfect for beginners — achievable at ~10 km/week",
        "milestones": [
            {"km": 200, "location": "Gander"},
            {"km": 500, "location": "Port aux Basques"}
        ]
    },
    "Tier 2 - The Eastern Challenge": {
        "total_km": 2000,
        "route": "St. John's → Québec City",
        "description": "Great for walkers, casual runners, or first-time big challenge",
        "milestones": [
            {"km": 1000, "location": "Halifax, NS"},
            {"km": 1500, "location": "Moncton, NB"},
            {"km": 2000, "location": "Québec City"}
        ]
    },
    "Tier 3 - The Central Challenge": {
        "total_km": 4000,
        "route": "St. John's → Toronto",
        "description": "Ambitious but doable in a year at ~80 km/week",
        "milestones": [
            {"km": 2500, "location": "Montréal"},
            {"km": 3000, "location": "Ottawa"},
            {"km": 3500, "location": "Sault Ste. Marie"},
            {"km": 4000, "location": "Toronto"}
        ]
    },
    "Tier 4 - The Prairies & Rockies": {
        "total_km": 6000,
        "route": "St. John's → Calgary",
        "description": "Ideal for advanced runners aiming for long-term consistency",
        "milestones": [
            {"km": 5000, "location": "Winnipeg"},
            {"km": 5500, "location": "Regina"},
            {"km": 6000, "location": "Calgary"}
        ]
    },
    "Tier 5 - The Full Coast-to-Coast": {
        "total_km": 7800,
        "route": "St. John's → Victoria",
        "description": "The ultimate Canadian journey — ~150 km/week, elite-level dedication",
        "milestones": [
            {"km": 7000, "location": "Kamloops"},
            {"km": 7500, "location": "Vancouver"},
            {"km": 7800, "location": "Victoria"}
        ]
    }
}

st.title("🍁 The Great Canadian Run")
st.write("Join The Great Canadian Run—a year-long journey from coast to coast. Track your kilometres, celebrate milestones, and explore Canada one step at a time.")

# Initialize session state
if "user_tier" not in st.session_state:
    st.session_state.user_tier = None
if "challenge_data" not in st.session_state:
    st.session_state.challenge_data = pd.DataFrame()

# Load user data
try:
    st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
except:
    st.session_state.challenge_data = pd.DataFrame()

# Check if user has joined a challenge
if st.session_state.user_tier is None:
    st.markdown("### Choose Your Challenge Tier")
    
    for tier_name, tier_info in CHALLENGE_TIERS.items():
        with st.expander(f"**{tier_name}** ({tier_info['total_km']} km)", expanded=False):
            st.write(f"**Route:** {tier_info['route']}")
            st.write(f"**Description:** {tier_info['description']}")
            
            st.write("**Milestones:**")
            for milestone in tier_info['milestones']:
                st.write(f"{milestone['icon']} {milestone['km']} km - {milestone['location']}")
            
            if st.button(f"Join {tier_name}", key=f"join_{tier_name}"):
                st.session_state.user_tier = tier_name
                st.success(f"Welcome to {tier_name}! Start tracking your progress.")
                st.rerun()

else:
    # User has joined a challenge - show progress
    tier_info = CHALLENGE_TIERS[st.session_state.user_tier]
    total_km = tier_info['total_km']
    
    # Calculate total distance logged from challenge data
    total_logged = 0
    if not st.session_state.challenge_data.empty:
        # Look for distance column in challenge data
        if 'distance_km' in st.session_state.challenge_data.columns:
            total_logged = st.session_state.challenge_data['distance_km'].fillna(0).astype(float).sum()
        elif len(st.session_state.challenge_data.columns) >= 2:
            # If column names are not detected, use the second column (index 1) as distance
            total_logged = st.session_state.challenge_data.iloc[:, 1].fillna(0).astype(float).sum()
    
    # Progress calculation
    progress_percentage = min((total_logged / total_km) * 100, 100)
    
    st.markdown(f"### Your Challenge: {st.session_state.user_tier}")
    st.write(f"**Route:** {tier_info['route']}")
    st.write(f"**Total Distance:** {total_km:,} km")
    st.write(f"**Your Progress:** {total_logged:,.1f} km / {total_km:,} km")
    
    # Progress bar
    st.progress(progress_percentage / 100)
    st.caption(f"Progress: {progress_percentage:.1f}%")
    
    # Milestone progress
    st.markdown("### 🎯 Milestone Progress")
    
    for milestone in tier_info['milestones']:
        milestone_km = milestone['km']
        milestone_progress = min((total_logged / milestone_km) * 100, 100) if milestone_km > 0 else 100
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"{milestone['icon']} **{milestone['location']}** ({milestone_km:,} km)")
            st.progress(milestone_progress / 100)
        with col2:
            if total_logged >= milestone_km:
                st.success("✅")
            else:
                remaining = milestone_km - total_logged
                st.caption(f"{remaining:,.0f} km to go")
    
    # Challenge completion
    if total_logged >= total_km:
        st.balloons()
        st.success("🎉 Congratulations! You've completed The Great Canadian Run!")
        st.markdown("### 🏆 Challenge Complete!")
        st.write("You've successfully journeyed from coast to coast across Canada!")
    
    # Log new activity
    st.markdown("### 📝 Log New Run")
    with st.form("log_activity"):
        activity_date = st.date_input("Date", value=date.today())
        distance = st.number_input("Distance (km)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Log Run"):
            if distance > 0:
                try:
                    ws.append_row([str(activity_date), distance])
                    st.success("Run logged successfully!")
                    # Refresh the challenge data
                    st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
                    st.rerun()
                except Exception as e:
                    st.error(f"Error logging run: {str(e)}")
    
    # Recent runs
    if not st.session_state.challenge_data.empty:
        st.markdown("### 📊 Recent Runs")
        st.dataframe(st.session_state.challenge_data.tail(10), use_container_width=True)
    
    # Reset challenge
    if st.button("🔄 Reset Challenge"):
        st.session_state.user_tier = None
        st.session_state.challenge_data = pd.DataFrame()
        st.rerun()
