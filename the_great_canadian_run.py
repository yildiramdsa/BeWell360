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
            {"km": 0, "location": "St. John's, NL", "description": "Start"},
            {"km": 100, "location": "Bishop's Falls, NL"},
            {"km": 200, "location": "Gander, NL"},
            {"km": 300, "location": "Grand Falls-Windsor, NL"},
            {"km": 400, "location": "Corner Brook, NL"},
            {"km": 500, "location": "Port aux Basques, NL", "description": "Tier 1 Complete – Ferry to Nova Scotia", "badge": "🥇 Atlantic Finisher"}
        ]
    },
    "Tier 2 - Eastern Challenge": {
        "total_km": 2000,
        "route": "St. John's → Québec City",
        "description": "Great for walkers, casual runners, or first-time big challenge",
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
        "route": "St. John's → Sault Ste. Marie",
        "description": "Ambitious but doable in a year at ~80 km/week",
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
        "route": "St. John's → Calgary",
        "description": "Ideal for advanced runners aiming for long-term consistency",
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
        "route": "St. John's → Victoria",
        "description": "The ultimate Canadian journey — ~150 km/week, elite-level dedication",
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

# Canadian fun facts for milestones
FUN_FACTS = {
    "Halifax": "Halifax has one of the world's largest natural harbors!",
    "Montréal": "Montréal is the second-largest French-speaking city in the world!",
    "Toronto": "Toronto is home to the CN Tower, one of the world's tallest free-standing structures!",
    "Winnipeg": "Winnipeg is known as the 'Gateway to the West' and has the longest skating rink in the world!",
    "Calgary": "Calgary hosts the world-famous Calgary Stampede, the 'Greatest Outdoor Show on Earth'!",
    "Vancouver": "Vancouver is consistently ranked as one of the world's most livable cities!",
    "Victoria": "Victoria is known as the 'Garden City' and has the mildest climate in Canada!"
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

# Hero Section
st.markdown("### 🏃‍♂️ Your Journey Progress")
st.write(f"**Total Distance:** {total_logged:,.0f} km / 7,800 km")
st.write("*Every kilometer takes you further across Canada.*")

# Progress bar
progress_percentage = min((total_logged / 7800) * 100, 100)
st.progress(progress_percentage / 100)
st.caption(f"Progress: {progress_percentage:.1f}%")

# Interactive map simulation (simplified visual representation)
st.markdown("### 🗺️ Your Journey Across Canada")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Simple progress visualization
    if total_logged < 500:
        st.write("📍 **Current Location:** Newfoundland")
        st.write("🎯 **Next Milestone:** Port aux Basques (500 km)")
    elif total_logged < 2000:
        st.write("📍 **Current Location:** Eastern Canada")
        st.write("🎯 **Next Milestone:** Québec City (2,000 km)")
    elif total_logged < 4000:
        st.write("📍 **Current Location:** Central Canada")
        st.write("🎯 **Next Milestone:** Sault Ste. Marie (4,000 km)")
    elif total_logged < 6000:
        st.write("📍 **Current Location:** Prairies & Rockies")
        st.write("🎯 **Next Milestone:** Calgary (6,000 km)")
    elif total_logged < 7800:
        st.write("📍 **Current Location:** British Columbia")
        st.write("🎯 **Next Milestone:** Victoria (7,800 km)")
    else:
        st.write("🏆 **Congratulations!** You've completed the coast-to-coast journey!")

# Challenge Tiers as Achievements
st.markdown("### 🏅 Challenge Achievements")

for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
    tier_completed = total_logged >= tier_info['total_km']
    
    if tier_completed:
        st.success(f"✅ **{tier_name}** - {tier_info['total_km']:,} km - COMPLETED!")
        if 'badge' in tier_info['checkpoints'][-1]:
            st.write(f"🏆 **Badge Unlocked:** {tier_info['checkpoints'][-1]['badge']}")
    else:
        remaining = tier_info['total_km'] - total_logged
        st.info(f"🎯 **{tier_name}** - {tier_info['total_km']:,} km - {remaining:,.0f} km to go")

# Detailed Checkpoints
st.markdown("### 🗺️ Journey Checkpoints")

for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
    with st.expander(f"**{tier_name}** ({tier_info['total_km']:,} km)", expanded=False):
        st.write(f"**Route:** {tier_info['route']}")
        st.write(f"**Description:** {tier_info['description']}")
        
        st.write("**Checkpoints:**")
        for checkpoint in tier_info['checkpoints']:
            if total_logged >= checkpoint['km']:
                st.write(f"✅ {checkpoint['km']:,} km - {checkpoint['location']}")
                if 'description' in checkpoint:
                    st.write(f"   *{checkpoint['description']}*")
                if 'badge' in checkpoint:
                    st.write(f"   🏆 **Badge:** {checkpoint['badge']}")
            else:
                remaining = checkpoint['km'] - total_logged
                st.write(f"⏳ {checkpoint['km']:,} km - {checkpoint['location']} ({remaining:,.0f} km to go)")

# Motivation & Rewards Section
st.markdown("### 🎉 Motivation & Rewards")

# Show unlocked badges
unlocked_badges = []
for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
    if total_logged >= tier_info['total_km']:
        if 'badge' in tier_info['checkpoints'][-1]:
            unlocked_badges.append(tier_info['checkpoints'][-1]['badge'])

if unlocked_badges:
    st.write("**🏆 Your Badges:**")
    for badge in unlocked_badges:
        st.write(f"  {badge}")
else:
    st.write("Keep running to unlock your first badge! 🏃‍♂️")

# Fun Facts
st.markdown("### 🇨🇦 Canadian Fun Facts")
for location, fact in FUN_FACTS.items():
    if any(location.lower() in checkpoint['location'].lower() for tier_info in CHALLENGE_CHECKPOINTS.values() for checkpoint in tier_info['checkpoints']):
        # Check if user has reached this location
        reached = any(total_logged >= checkpoint['km'] and location.lower() in checkpoint['location'].lower() 
                     for tier_info in CHALLENGE_CHECKPOINTS.values() for checkpoint in tier_info['checkpoints'])
        if reached:
            st.write(f"**{location}:** {fact}")

# Log Your Kilometers
st.markdown("### 📝 Log Your Kilometers")
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

# Recent runs
if not st.session_state.challenge_data.empty:
    st.markdown("### 📊 Recent Runs")
    st.dataframe(st.session_state.challenge_data.tail(10), use_container_width=True)

# Challenge completion celebration
if total_logged >= 7800:
    st.balloons()
    st.success("🎉 Congratulations! You've completed The Great Canadian Run!")
    st.markdown("### 🏆 Coast-to-Coast Finisher!")
    st.write("You've successfully journeyed from St. John's to Victoria across Canada!")