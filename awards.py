import streamlit as st
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

# ---------------- Badge Data ----------------
BADGES = {
    "Atlantic Explorer": {
        "description": "Completed the Atlantic Challenge - 500 km journey from St. John's to Port aux Basques",
        "challenge": "Atlantic Challenge",
        "requirements": "Log 500 km",
        "icon": "🍁",
        "route": "St. John's → Port aux Basques"
    },
    "Eastern Adventurer": {
        "description": "Completed the Eastern Challenge - 2,000 km journey through Nova Scotia, New Brunswick, and Quebec",
        "challenge": "Eastern Challenge", 
        "requirements": "Log 2,000 km",
        "icon": "🍁",
        "route": "Port aux Basques → Québec City"
    },
    "Central Trailblazer": {
        "description": "Completed the Central Challenge - 4,000 km journey through Quebec and Ontario",
        "challenge": "Central Challenge",
        "requirements": "Log 4,000 km", 
        "icon": "🍁",
        "route": "Québec City → Sault Ste. Marie"
    },
    "Prairie Voyager": {
        "description": "Completed the Prairies & Rockies Challenge - 6,000 km journey across the Prairies to Calgary",
        "challenge": "Prairies & Rockies",
        "requirements": "Log 6,000 km",
        "icon": "🍁", 
        "route": "Sault Ste. Marie → Calgary"
    },
    "True North Finisher": {
        "description": "Completed the Full Coast-to-Coast Challenge - 7,800 km journey from coast to coast",
        "challenge": "Full Coast-to-Coast",
        "requirements": "Log 7,800 km",
        "icon": "🏆",
        "route": "Calgary → Victoria"
    }
}

st.title("🏆 Awards & Badges")
st.write("Celebrate your achievements and track your progress across all challenges.")

# Get user's total logged distance
try:
    ws = client.open("the_great_canadian_run").sheet1
    challenge_data = ws.get_all_records()
    
    if challenge_data and 'distance_km' in challenge_data[0]:
        total_logged = sum(float(record.get('distance_km', 0) or 0) for record in challenge_data)
    else:
        total_logged = 0
except:
    total_logged = 0

# ---------------- Badge Display ----------------
st.markdown("### Your Badges")

col1, col2 = st.columns([3, 1])

with col1:
    st.write(f"**Total Distance Logged:** {total_logged:,.0f} km")
    
with col2:
    # Calculate completion percentage
    max_distance = 7800
    completion_pct = min((total_logged / max_distance) * 100, 100)
    st.metric("Journey Progress", f"{completion_pct:.1f}%")

st.markdown("---")

# Display badges
for badge_name, badge_info in BADGES.items():
    # Check if badge is earned
    if badge_name == "Atlantic Explorer":
        earned = total_logged >= 500
    elif badge_name == "Eastern Adventurer":
        earned = total_logged >= 2000
    elif badge_name == "Central Trailblazer":
        earned = total_logged >= 4000
    elif badge_name == "Prairie Voyager":
        earned = total_logged >= 6000
    elif badge_name == "True North Finisher":
        earned = total_logged >= 7800
    else:
        earned = False
    
    # Create badge container
    if earned:
        st.markdown(f"""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f0f8f0;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 2em;">{badge_info['icon']}</div>
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #2E7D32;">✅ {badge_name}</h4>
                    <p style="margin: 5px 0; color: #666;">{badge_info['description']}</p>
                    <div style="font-size: 0.9em; color: #888;">
                        <strong>Challenge:</strong> {badge_info['challenge']}<br>
                        <strong>Route:</strong> {badge_info['route']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="border: 2px solid #E0E0E0; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; opacity: 0.6;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 2em; filter: grayscale(100%);">{badge_info['icon']}</div>
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #999;">🔒 {badge_name}</h4>
                    <p style="margin: 5px 0; color: #999;">{badge_info['description']}</p>
                    <div style="font-size: 0.9em; color: #bbb;">
                        <strong>Challenge:</strong> {badge_info['challenge']}<br>
                        <strong>Requirements:</strong> {badge_info['requirements']}<br>
                        <strong>Route:</strong> {badge_info['route']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- Progress Summary ----------------
st.markdown("---")
st.markdown("### Challenge Progress")

# Show progress for each challenge tier
challenge_tiers = [
    {"name": "Atlantic Challenge", "target": 500, "badge": "Atlantic Explorer"},
    {"name": "Eastern Challenge", "target": 2000, "badge": "Eastern Adventurer"}, 
    {"name": "Central Challenge", "target": 4000, "badge": "Central Trailblazer"},
    {"name": "Prairies & Rockies", "target": 6000, "badge": "Prairie Voyager"},
    {"name": "Full Coast-to-Coast", "target": 7800, "badge": "True North Finisher"}
]

for tier in challenge_tiers:
    tier_progress = min((total_logged / tier['target']) * 100, 100)
    tier_completed = total_logged >= tier['target']
    
    if tier_completed:
        st.markdown(f"✅ **{tier['name']}** - {tier['target']:,} km - COMPLETED! 🎖 {tier['badge']}")
    else:
        remaining = tier['target'] - total_logged
        st.markdown(f"⏳ **{tier['name']}** - {tier['target']:,} km - {remaining:,} km to go")
    
    st.progress(tier_progress / 100)
    st.write("")

# ---------------- Links ----------------
st.markdown("---")
st.markdown("### Keep Going!")

col1, col2 = st.columns(2)

with col1:
    if st.button("🏃‍♂️ Continue Your Journey", use_container_width=True):
        st.switch_page("the_great_canadian_run.py")

with col2:
    if st.button("📊 View All Challenges", use_container_width=True):
        st.switch_page("the_great_canadian_run.py")

# ---------------- Footer Info ----------------
st.markdown("---")
st.markdown("""
**How to earn badges:**
- Log your running kilometers in The Great Canadian Run
- Complete each challenge tier to unlock the corresponding badge
- Track your progress and celebrate your achievements!

*Badges are automatically awarded when you reach the required distance milestones.*
""")
