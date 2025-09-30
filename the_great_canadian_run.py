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

# Challenge configuration with detailed checkpoints
CHALLENGE_CHECKPOINTS = {
    "Atlantic Challenge": {
        "total_km": 500,
        "route": "St. John's → Port aux Basques",
        "description": "Perfect for beginners — ~10 km/week",
        "checkpoints": [
            {"km": 0, "location": "St. John's, NL"},
            {"km": 100, "location": "Bishop's Falls, NL"},
            {"km": 200, "location": "Gander, NL"},
            {"km": 300, "location": "Grand Falls-Windsor, NL"},
            {"km": 400, "location": "Corner Brook, NL"},
            {"km": 500, "location": "Port aux Basques, NL", "description": "Ferry to Nova Scotia", "badge": "🍁 Atlantic Explorer"}
        ]
    },
    "Eastern Challenge": {
        "total_km": 2000,
        "route": "Port aux Basques → Québec City",
        "description": "Travel through Nova Scotia, New Brunswick, and into Québec. City checkpoints, such as Halifax, Moncton, and Québec City, keep your progress visible and motivating.",
        "checkpoints": [
            {"km": 500, "location": "Newfoundland"},
            {"km": 600, "location": "Enter Nova Scotia"},
            {"km": 700, "location": "Yarmouth, NS"},
            {"km": 1000, "location": "Halifax, NS"},
            {"km": 1150, "location": "Truro, NS"},
            {"km": 1300, "location": "Cross into New Brunswick"},
            {"km": 1500, "location": "Moncton, NB"},
            {"km": 1650, "location": "Fredericton, NB"},
            {"km": 1800, "location": "Cross into Quebec"},
            {"km": 2000, "location": "Québec City, QC", "description": "Eastern Challenge", "badge": "🍁 Eastern Adventurer"}
        ]
    },
    "Central Challenge": {
        "total_km": 4000,
        "route": "Québec City → Sault Ste. Marie",
        "description": "Cross Québec into Ontario. Major milestones in Montréal, Ottawa, and Toronto mark steady growth and endurance.",
        "checkpoints": [
            {"km": 2000, "location": "Québec City, QC"},
            {"km": 2250, "location": "Trois-Rivières, QC"},
            {"km": 2500, "location": "Montréal, QC"},
            {"km": 2650, "location": "Cross into Ontario"},
            {"km": 3000, "location": "Ottawa, ON"},
            {"km": 3250, "location": "Kingston, ON"},
            {"km": 3500, "location": "Toronto, ON", "description": "Central Challenge", "badge": "🍁 Central Trailblazer"},
            {"km": 4000, "location": "Sault Ste. Marie, ON"}
        ]
    },
    "Prairies & Rockies": {
        "total_km": 6000,
        "route": "Sault Ste. Marie → Calgary",
        "description": "Move across the Prairies into the Rocky Mountains. Celebrate key milestones in Winnipeg, Regina, and Calgary as you head west to the western provinces.",
        "checkpoints": [
            {"km": 4000, "location": "Sault Ste. Marie, ON"},
            {"km": 4250, "location": "Thunder Bay, ON"},
            {"km": 4500, "location": "Enter Manitoba"},
            {"km": 5000, "location": "Winnipeg, MB"},
            {"km": 5250, "location": "Brandon, MB"},
            {"km": 5500, "location": "Regina, SK"},
            {"km": 5750, "location": "Moose Jaw, SK"},
            {"km": 6000, "location": "Calgary, AB", "description": "Prairies & Rockies", "badge": "🍁 Prairies & Rockies Runner"}
        ]
    },
    "Full Coast-to-Coast": {
        "total_km": 7800,
        "route": "Calgary → Victoria",
        "description": "Enter British Columbia and the Rockies' final stretch. Complete the journey in Kamloops, Vancouver, and Victoria, achieving coast-to-coast success.",
        "checkpoints": [
            {"km": 6000, "location": "Calgary, AB"},
            {"km": 6250, "location": "Banff, AB"},
            {"km": 6500, "location": "Kicking Horse Pass, AB"},
            {"km": 6700, "location": "Enter British Columbia"},
            {"km": 7000, "location": "Kamloops, BC"},
            {"km": 7250, "location": "Hope, BC"},
            {"km": 7500, "location": "Vancouver, BC"},
            {"km": 7800, "location": "Victoria, BC", "description": "Finish Line", "badge": "🍁 Coast-to-Coast Champion"}
        ]
    }
}


st.title("🍁 The Great Canadian Run")

# Initialize session state
if "challenge_data" not in st.session_state:
    st.session_state.challenge_data = pd.DataFrame()

# Load user data
try:
    st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
except:
    st.session_state.challenge_data = pd.DataFrame()

# Calculate total distance logged
total_logged = 0
if not st.session_state.challenge_data.empty:
    if 'distance_km' in st.session_state.challenge_data.columns:
        total_logged = st.session_state.challenge_data['distance_km'].fillna(0).astype(float).sum()
    elif len(st.session_state.challenge_data.columns) >= 2:
        total_logged = st.session_state.challenge_data.iloc[:, 1].fillna(0).astype(float).sum()

# Main Progress Section
st.markdown("### Your Journey Progress")

# Progress information grouped together
col1, col2, col3 = st.columns(3)

with col1:
    st.write(f"**Total Distance:** {total_logged:,.0f} km")

with col2:
    if total_logged < 100:
        st.write("**Current Location:** St. John's, NL")
    elif total_logged < 200:
        st.write("**Current Location:** Bishop's Falls, NL")
    elif total_logged < 300:
        st.write("**Current Location:** Gander, NL")
    elif total_logged < 400:
        st.write("**Current Location:** Grand Falls-Windsor, NL")
    elif total_logged < 500:
        st.write("**Current Location:** Corner Brook, NL")
    elif total_logged < 600:
        st.write("**Current Location:** Port aux Basques, NL")
    elif total_logged < 700:
        st.write("**Current Location:** Enter Nova Scotia")
    elif total_logged < 1000:
        st.write("**Current Location:** Yarmouth, NS")
    elif total_logged < 1150:
        st.write("**Current Location:** Halifax, NS")
    elif total_logged < 1300:
        st.write("**Current Location:** Truro, NS")
    elif total_logged < 1500:
        st.write("**Current Location:** Cross into New Brunswick")
    elif total_logged < 1650:
        st.write("**Current Location:** Moncton, NB")
    elif total_logged < 1800:
        st.write("**Current Location:** Fredericton, NB")
    elif total_logged < 2000:
        st.write("**Current Location:** Cross into Quebec")
    elif total_logged < 2250:
        st.write("**Current Location:** Québec City, QC")
    elif total_logged < 2500:
        st.write("**Current Location:** Trois-Rivières, QC")
    elif total_logged < 2650:
        st.write("**Current Location:** Montréal, QC")
    elif total_logged < 3000:
        st.write("**Current Location:** Cross into Ontario")
    elif total_logged < 3250:
        st.write("**Current Location:** Ottawa, ON")
    elif total_logged < 3500:
        st.write("**Current Location:** Kingston, ON")
    elif total_logged < 4000:
        st.write("**Current Location:** Toronto, ON")
    elif total_logged < 4250:
        st.write("**Current Location:** Sault Ste. Marie, ON")
    elif total_logged < 4500:
        st.write("**Current Location:** Thunder Bay, ON")
    elif total_logged < 5000:
        st.write("**Current Location:** Enter Manitoba")
    elif total_logged < 5250:
        st.write("**Current Location:** Winnipeg, MB")
    elif total_logged < 5500:
        st.write("**Current Location:** Brandon, MB")
    elif total_logged < 5750:
        st.write("**Current Location:** Regina, SK")
    elif total_logged < 6000:
        st.write("**Current Location:** Moose Jaw, SK")
    elif total_logged < 6250:
        st.write("**Current Location:** Calgary, AB")
    elif total_logged < 6500:
        st.write("**Current Location:** Banff, AB")
    elif total_logged < 6700:
        st.write("**Current Location:** Kicking Horse Pass, AB")
    elif total_logged < 7000:
        st.write("**Current Location:** Enter British Columbia")
    elif total_logged < 7250:
        st.write("**Current Location:** Kamloops, BC")
    elif total_logged < 7500:
        st.write("**Current Location:** Hope, BC")
    elif total_logged < 7800:
        st.write("**Current Location:** Vancouver, BC")
    else:
        st.write("**Current Location:** Victoria, BC")

with col3:
    if total_logged < 100:
        st.write("**Next Milestone:** Bishop's Falls, NL (100 km)")
    elif total_logged < 200:
        st.write("**Next Milestone:** Gander, NL (200 km)")
    elif total_logged < 300:
        st.write("**Next Milestone:** Grand Falls-Windsor, NL (300 km)")
    elif total_logged < 400:
        st.write("**Next Milestone:** Corner Brook, NL (400 km)")
    elif total_logged < 500:
        st.write("**Next Milestone:** Port aux Basques, NL (500 km)")
    elif total_logged < 600:
        st.write("**Next Milestone:** Enter Nova Scotia (600 km)")
    elif total_logged < 700:
        st.write("**Next Milestone:** Yarmouth, NS (700 km)")
    elif total_logged < 1000:
        st.write("**Next Milestone:** Halifax, NS (1,000 km)")
    elif total_logged < 1150:
        st.write("**Next Milestone:** Truro, NS (1,150 km)")
    elif total_logged < 1300:
        st.write("**Next Milestone:** Cross into New Brunswick (1,300 km)")
    elif total_logged < 1500:
        st.write("**Next Milestone:** Moncton, NB (1,500 km)")
    elif total_logged < 1650:
        st.write("**Next Milestone:** Fredericton, NB (1,650 km)")
    elif total_logged < 1800:
        st.write("**Next Milestone:** Cross into Quebec (1,800 km)")
    elif total_logged < 2000:
        st.write("**Next Milestone:** Québec City, QC (2,000 km)")
    elif total_logged < 2250:
        st.write("**Next Milestone:** Trois-Rivières, QC (2,250 km)")
    elif total_logged < 2500:
        st.write("**Next Milestone:** Montréal, QC (2,500 km)")
    elif total_logged < 2650:
        st.write("**Next Milestone:** Cross into Ontario (2,650 km)")
    elif total_logged < 3000:
        st.write("**Next Milestone:** Ottawa, ON (3,000 km)")
    elif total_logged < 3250:
        st.write("**Next Milestone:** Kingston, ON (3,250 km)")
    elif total_logged < 3500:
        st.write("**Next Milestone:** Toronto, ON (3,500 km)")
    elif total_logged < 4000:
        st.write("**Next Milestone:** Sault Ste. Marie, ON (4,000 km)")
    elif total_logged < 4250:
        st.write("**Next Milestone:** Thunder Bay, ON (4,250 km)")
    elif total_logged < 4500:
        st.write("**Next Milestone:** Enter Manitoba (4,500 km)")
    elif total_logged < 5000:
        st.write("**Next Milestone:** Winnipeg, MB (5,000 km)")
    elif total_logged < 5250:
        st.write("**Next Milestone:** Brandon, MB (5,250 km)")
    elif total_logged < 5500:
        st.write("**Next Milestone:** Regina, SK (5,500 km)")
    elif total_logged < 5750:
        st.write("**Next Milestone:** Moose Jaw, SK (5,750 km)")
    elif total_logged < 6000:
        st.write("**Next Milestone:** Calgary, AB (6,000 km)")
    elif total_logged < 6250:
        st.write("**Next Milestone:** Banff, AB (6,250 km)")
    elif total_logged < 6500:
        st.write("**Next Milestone:** Kicking Horse Pass, AB (6,500 km)")
    elif total_logged < 6700:
        st.write("**Next Milestone:** Enter British Columbia (6,700 km)")
    elif total_logged < 7000:
        st.write("**Next Milestone:** Kamloops, BC (7,000 km)")
    elif total_logged < 7250:
        st.write("**Next Milestone:** Hope, BC (7,250 km)")
    elif total_logged < 7500:
        st.write("**Next Milestone:** Vancouver, BC (7,500 km)")
    elif total_logged < 7800:
        st.write("**Next Milestone:** Victoria, BC (7,800 km)")
    else:
        st.write("**Status:** Journey Complete!")


# Progress bar
progress_percentage = min((total_logged / 7800) * 100, 100)
st.progress(progress_percentage / 100)
st.caption(f"Progress: {progress_percentage:.1f}%")

# Completion celebration
if total_logged >= 7800:
    st.write("**Congratulations!** You've completed the coast-to-coast journey!")

# Log Your Kilometers
st.markdown("### Log Your Kilometers")
with st.form("log_run"):
    activity_date = st.date_input("Date", value=date.today())
    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1)
    
    if st.form_submit_button("Log Run"):
        if distance > 0:
            try:
                ws.append_row([str(activity_date), distance])
                st.success("Run logged successfully!")
                st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
                st.rerun()
            except Exception as e:
                st.error(f"Error logging run: {str(e)}")

# Recent Runs
if not st.session_state.challenge_data.empty:
    with st.expander("Recent Runs", expanded=False):
        st.dataframe(st.session_state.challenge_data.tail(10), use_container_width=True)

# Challenge Progress
st.markdown("### Challenge Progress")
for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
    tier_completed = total_logged >= tier_info['total_km']
    
    # Combined achievement status and checkpoints in one expander
    if tier_completed:
        if 'badge' in tier_info['checkpoints'][-1]:
            status_text = f"✅ {tier_name} | {tier_info['total_km']:,} km | {tier_info['checkpoints'][-1]['badge']}"
        else:
            status_text = f"✅ {tier_name} | {tier_info['total_km']:,} km"
    else:
        remaining = tier_info['total_km'] - total_logged
        status_text = f"⏳ {tier_name} | {tier_info['total_km']:,} km"
    
    with st.expander(status_text, expanded=False):
        # Route
        st.markdown(f"Route: {tier_info['route']}")
        
        # Badge
        if 'badge' in tier_info['checkpoints'][-1]:
            st.markdown(f"Badge: {tier_info['checkpoints'][-1]['badge']}")
        
        st.markdown("Checkpoints:")
        
        # Checkpoints in a more organized format
        for i, checkpoint in enumerate(tier_info['checkpoints']):
            remaining_to_tier = tier_info['total_km'] - checkpoint['km']
            st.markdown(f"{checkpoint['km']:,} km – {checkpoint['location']} | {remaining_to_tier:,} km to go")
            
            # Add spacing between checkpoints (except for the last one)
            if i < len(tier_info['checkpoints']) - 1:
                st.markdown("")

# Challenge completion celebration
if total_logged >= 7800:
    st.balloons()
    st.success("Congratulations! You've completed The Great Canadian Run!")
    st.markdown("### Coast-to-Coast Finisher!")
    st.write("You've successfully journeyed from St. John's to Victoria across Canada!")