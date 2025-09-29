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
    "Tier 1 - Atlantic Challenge": {
        "total_km": 500,
        "route": "St. John's → Port aux Basques",
        "description": "Perfect for beginners — ~10 km/week",
        "checkpoints": [
            {"km": 0, "location": "St. John's, NL"},
            {"km": 100, "location": "Bishop's Falls, NL"},
            {"km": 200, "location": "Gander, NL"},
            {"km": 300, "location": "Grand Falls-Windsor, NL"},
            {"km": 400, "location": "Corner Brook, NL"},
            {"km": 500, "location": "Port aux Basques, NL", "description": "Tier 1 Complete – Ferry to Nova Scotia", "badge": "🥇 Atlantic Finisher"}
        ]
    },
    "Tier 2 - Eastern Challenge": {
        "total_km": 2000,
        "route": "Port aux Basques → Québec City",
        "description": "Travel through Nova Scotia, New Brunswick, and into Québec. City checkpoints, such as Halifax, Moncton, and Québec City, keep your progress visible and motivating.",
        "checkpoints": [
            {"km": 500, "location": "Newfoundland complete"},
            {"km": 600, "location": "Enter Nova Scotia"},
            {"km": 700, "location": "Yarmouth, NS"},
            {"km": 1000, "location": "Halifax, NS"},
            {"km": 1150, "location": "Truro, NS"},
            {"km": 1300, "location": "Cross into New Brunswick"},
            {"km": 1500, "location": "Moncton, NB"},
            {"km": 1650, "location": "Fredericton, NB"},
            {"km": 1800, "location": "Cross into Quebec"},
            {"km": 2000, "location": "Québec City, QC", "description": "Tier 2 Complete", "badge": "🥇 Eastern Explorer"}
        ]
    },
    "Tier 3 - Central Challenge": {
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
            {"km": 3500, "location": "Toronto, ON", "description": "Tier 3 Complete"},
            {"km": 4000, "location": "Sault Ste. Marie, ON"}
        ]
    },
    "Tier 4 - Prairies & Rockies": {
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
            {"km": 6000, "location": "Calgary, AB", "description": "Tier 4 Complete", "badge": "🥇 Prairie & Rockies Runner"}
        ]
    },
    "Tier 5 - Full Coast-to-Coast": {
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
            {"km": 7800, "location": "Victoria, BC", "description": "Tier 5 Complete – Finish Line", "badge": "🏆 Coast-to-Coast Finisher"}
        ]
    }
}


st.title("🍁 The Great Canadian Run")
st.subheader("A virtual journey across Canada — one step at a time.")

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
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Your Journey Progress")
    st.write(f"**Total Distance:** {total_logged:,.0f} km / 7,800 km")
    st.write("*Every kilometer takes you further across Canada.*")
    
    # Progress bar
    progress_percentage = min((total_logged / 7800) * 100, 100)
    st.progress(progress_percentage / 100)
    st.caption(f"Progress: {progress_percentage:.1f}%")
    
    # Current location
    if total_logged < 500:
        st.write("**Current Location:** Newfoundland")
        st.write("**Next Milestone:** Port aux Basques (500 km)")
    elif total_logged < 2000:
        st.write("**Current Location:** Eastern Canada")
        st.write("**Next Milestone:** Québec City (2,000 km)")
    elif total_logged < 4000:
        st.write("**Current Location:** Central Canada")
        st.write("**Next Milestone:** Sault Ste. Marie (4,000 km)")
    elif total_logged < 6000:
        st.write("**Current Location:** Prairies & Rockies")
        st.write("**Next Milestone:** Calgary (6,000 km)")
    elif total_logged < 7800:
        st.write("**Current Location:** British Columbia")
        st.write("**Next Milestone:** Victoria (7,800 km)")
    else:
        st.write("**Congratulations!** You've completed the coast-to-coast journey!")

with col2:
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

# Challenge Progress & Recent Runs
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Challenge Progress")
    for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
        tier_completed = total_logged >= tier_info['total_km']
        
        # Combined achievement status and checkpoints in one expander
        if tier_completed:
            status_text = f"**{tier_name}** - {tier_info['total_km']:,} km - COMPLETED!"
            if 'badge' in tier_info['checkpoints'][-1]:
                status_text += f" | **Badge:** {tier_info['checkpoints'][-1]['badge']}"
        else:
            remaining = tier_info['total_km'] - total_logged
            status_text = f"**{tier_name}** - {tier_info['total_km']:,} km - {remaining:,.0f} km to go"
        
        with st.expander(status_text, expanded=False):
            # Route only
            st.markdown(f"**Route:** {tier_info['route']}")
            
            st.markdown("**Checkpoints:**")
            
            # Checkpoints in a more organized format
            for i, checkpoint in enumerate(tier_info['checkpoints']):
                checkpoint_reached = total_logged >= checkpoint['km']
                
                if checkpoint_reached:
                    st.markdown(f"✅ **{checkpoint['km']:,} km** - {checkpoint['location']}")
                    if 'description' in checkpoint:
                        st.markdown(f"   *{checkpoint['description']}*")
                    if 'badge' in checkpoint:
                        st.markdown(f"   🏆 **Badge:** {checkpoint['badge']}")
                else:
                    remaining = checkpoint['km'] - total_logged
                    st.markdown(f"⏳ **{checkpoint['km']:,} km** - {checkpoint['location']} (*{remaining:,.0f} km to go*)")
                
                # Add spacing between checkpoints (except for the last one)
                if i < len(tier_info['checkpoints']) - 1:
                    st.markdown("")

with col2:
    if not st.session_state.challenge_data.empty:
        st.markdown("### Recent Runs")
        st.dataframe(st.session_state.challenge_data.tail(10), use_container_width=True)

# Challenge completion celebration
if total_logged >= 7800:
    st.balloons()
    st.success("Congratulations! You've completed The Great Canadian Run!")
    st.markdown("### Coast-to-Coast Finisher!")
    st.write("You've successfully journeyed from St. John's to Victoria across Canada!")