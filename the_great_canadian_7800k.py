import streamlit as st
import pandas as pd
from datetime import date
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
ws = client.open("the_great_canadian_7800k").sheet1

# Challenge configuration with detailed checkpoints
CHALLENGE_CHECKPOINTS = {
    "Atlantic Challenge": {
        "total_km": 500,
        "route": "St. John's → Port aux Basques",
        "description": "Perfect for beginners — ~10 km/week",
        "checkpoints": [
            {"km": 0, "location": "St. John's, NL"},
            {"km": 200, "location": "Gander, NL"},
            {"km": 300, "location": "Grand Falls-Windsor, NL"},
            {"km": 400, "location": "Corner Brook, NL"},
            {"km": 500, "location": "Port aux Basques, NL", "badge": "Atlantic Explorer"}
        ]
    },
    "Eastern Challenge": {
        "total_km": 2000,
        "route": "Port aux Basques → Québec City",
        "description": "Travel through Nova Scotia, New Brunswick, and into Québec.",
        "checkpoints": [
            {"km": 600, "location": "Sydney, NS"},
            {"km": 1000, "location": "Halifax, NS"},
            {"km": 1300, "location": "Enter New Brunswick"},
            {"km": 1500, "location": "Moncton, NB"},
            {"km": 1650, "location": "Fredericton, NB"},
            {"km": 1800, "location": "Enter Quebec"},
            {"km": 2000, "location": "Québec City, QC", "badge": "Eastern Adventurer"}
        ]
    },
    "Central Challenge": {
        "total_km": 4000,
        "route": "Québec City → Sault Ste. Marie",
        "description": "Cross Québec into Ontario. Major milestones in Montréal, Ottawa, and Toronto.",
        "checkpoints": [
            {"km": 2250, "location": "Trois-Rivières, QC"},
            {"km": 2500, "location": "Montréal, QC"},
            {"km": 2650, "location": "Enter Ontario"},
            {"km": 3000, "location": "Ottawa, ON"},
            {"km": 3250, "location": "Kingston, ON"},
            {"km": 3500, "location": "Toronto, ON"},
            {"km": 4000, "location": "Sault Ste. Marie, ON", "badge": "Central Challenger"}
        ]
    },
    "Prairies & Rockies": {
        "total_km": 6000,
        "route": "Sault Ste. Marie → Calgary",
        "description": "Move across the Prairies into the Rocky Mountains.",
        "checkpoints": [
            {"km": 4250, "location": "Thunder Bay, ON"},
            {"km": 4500, "location": "Enter Manitoba"},
            {"km": 5000, "location": "Winnipeg, MB"},
            {"km": 5250, "location": "Brandon, MB"},
            {"km": 5500, "location": "Regina, SK"},
            {"km": 5750, "location": "Moose Jaw, SK"},
            {"km": 6000, "location": "Calgary, AB", "badge": "Prairie Voyager"}
        ]
    },
    "Full Coast-to-Coast": {
        "total_km": 7800,
        "route": "Calgary → Victoria",
        "description": "Enter British Columbia. Complete the journey in Kamloops, Vancouver, and Victoria.",
        "checkpoints": [
            {"km": 6250, "location": "Banff, AB"},
            {"km": 6500, "location": "Kicking Horse Pass (AB/BC border)"},
            {"km": 7000, "location": "Kamloops, BC"},
            {"km": 7250, "location": "Hope, BC"},
            {"km": 7500, "location": "Vancouver, BC"},
            {"km": 7800, "location": "Victoria, BC", "badge": "True North Finisher"}
        ]
    }
}

st.title("🍁 The Great Canadian 7,800K")

st.info(
    "**Did you know?**\n\nThe total distance across Canada from St. John's, NL to Victoria, BC is approximately 7,800 km.\n\n"
    "To celebrate this coast-to-coast journey, log 7,800 km in total using distance-based activities such as running, walking, cycling, hiking, or any activity that tracks distance."
)

# Initialize session state
if "challenge_data" not in st.session_state:
    st.session_state.challenge_data = pd.DataFrame()

# Load user data
try:
    st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
except Exception:
    st.session_state.challenge_data = pd.DataFrame()

# Calculate total distance logged
total_logged = 0
if not st.session_state.challenge_data.empty:
    if "distance_km" in st.session_state.challenge_data.columns:
        total_logged = st.session_state.challenge_data["distance_km"].fillna(0).astype(float).sum()
    elif len(st.session_state.challenge_data.columns) >= 2:
        total_logged = st.session_state.challenge_data.iloc[:, 1].fillna(0).astype(float).sum()

st.markdown("### Your Journey Progress")

col1, col2, col3 = st.columns(3)
with col1:
    st.write(f"**Total Distance:** {total_logged:,.0f} km")
with col2:
    if total_logged < 200:
        st.write("**Current Location:** St. John's, NL")
    elif total_logged < 300:
        st.write("**Current Location:** Gander, NL")
    elif total_logged < 400:
        st.write("**Current Location:** Grand Falls-Windsor, NL")
    elif total_logged < 500:
        st.write("**Current Location:** Corner Brook, NL")
    elif total_logged < 600:
        st.write("**Current Location:** Port aux Basques, NL")
    elif total_logged < 1000:
        st.write("**Current Location:** Sydney, NS")
    elif total_logged < 1300:
        st.write("**Current Location:** Halifax, NS")
    elif total_logged < 1500:
        st.write("**Current Location:** Enter New Brunswick")
    elif total_logged < 1650:
        st.write("**Current Location:** Moncton, NB")
    elif total_logged < 1800:
        st.write("**Current Location:** Fredericton, NB")
    elif total_logged < 2000:
        st.write("**Current Location:** Enter Quebec")
    elif total_logged < 2250:
        st.write("**Current Location:** Québec City, QC")
    elif total_logged < 2500:
        st.write("**Current Location:** Trois-Rivières, QC")
    elif total_logged < 2650:
        st.write("**Current Location:** Montréal, QC")
    elif total_logged < 3000:
        st.write("**Current Location:** Enter Ontario")
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
    elif total_logged < 7000:
        st.write("**Current Location:** Kicking Horse Pass (AB/BC border)")
    elif total_logged < 7250:
        st.write("**Current Location:** Kamloops, BC")
    elif total_logged < 7500:
        st.write("**Current Location:** Hope, BC")
    elif total_logged < 7800:
        st.write("**Current Location:** Vancouver, BC")
    else:
        st.write("**Current Location:** Victoria, BC")
with col3:
    if total_logged < 200:
        st.write("**Next Milestone:** Gander, NL (200 km)")
    elif total_logged < 300:
        st.write("**Next Milestone:** Grand Falls-Windsor, NL (300 km)")
    elif total_logged < 400:
        st.write("**Next Milestone:** Corner Brook, NL (400 km)")
    elif total_logged < 500:
        st.write("**Next Milestone:** Port aux Basques, NL (500 km)")
    elif total_logged < 600:
        st.write("**Next Milestone:** Sydney, NS (600 km)")
    elif total_logged < 1000:
        st.write("**Next Milestone:** Halifax, NS (1,000 km)")
    elif total_logged < 1300:
        st.write("**Next Milestone:** Enter New Brunswick (1,300 km)")
    elif total_logged < 1500:
        st.write("**Next Milestone:** Moncton, NB (1,500 km)")
    elif total_logged < 1650:
        st.write("**Next Milestone:** Fredericton, NB (1,650 km)")
    elif total_logged < 1800:
        st.write("**Next Milestone:** Enter Quebec (1,800 km)")
    elif total_logged < 2000:
        st.write("**Next Milestone:** Québec City, QC (2,000 km)")
    elif total_logged < 2250:
        st.write("**Next Milestone:** Trois-Rivières, QC (2,250 km)")
    elif total_logged < 2500:
        st.write("**Next Milestone:** Montréal, QC (2,500 km)")
    elif total_logged < 2650:
        st.write("**Next Milestone:** Enter Ontario (2,650 km)")
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
        st.write("**Next Milestone:** Kicking Horse Pass (6,500 km)")
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

if total_logged >= 7800:
    st.write("**Congratulations!** You've completed the coast-to-coast journey!")

st.markdown("### Log Your Kilometers")


def get_existing_distance(selected_date):
    date_str = str(selected_date)
    existing_data = st.session_state.challenge_data
    if not existing_data.empty and "date" in existing_data.columns:
        date_exists = existing_data["date"].astype(str).str.contains(date_str).any()
        if date_exists:
            row = existing_data[existing_data["date"].astype(str) == date_str].iloc[0]
            if "distance_km" in existing_data.columns:
                return float(row["distance_km"]) if pd.notna(row["distance_km"]) else 0.0
            return float(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else 0.0
    return 0.0


activity_date = st.date_input("Date", value=date.today())
existing_distance = get_existing_distance(activity_date)

if existing_distance > 0:
    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=existing_distance,
                               help=f"Currently logged: {existing_distance} km for {activity_date}")
else:
    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=0.0,
                               help="No run logged for this date")

if st.button("Log Run"):
    if distance > 0:
        try:
            date_str = str(activity_date)
            existing_data = st.session_state.challenge_data

            if not existing_data.empty and "date" in existing_data.columns:
                date_exists = existing_data["date"].astype(str).str.contains(date_str).any()
                if date_exists:
                    row_index = existing_data[existing_data["date"].astype(str) == date_str].index[0]
                    if "distance_km" in existing_data.columns:
                        ws.update(f"B{row_index + 2}", [[distance]])
                    else:
                        ws.update(f"A{row_index + 2}:B{row_index + 2}", [[date_str, distance]])
                    st.success(f"Updated run for {activity_date}!")
                else:
                    ws.append_row([date_str, distance])
                    st.success("Run logged successfully!")
            else:
                ws.append_row([date_str, distance])
                st.success("Run logged successfully!")

            st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
            st.rerun()
        except Exception as e:
            st.error(f"Error logging run: {str(e)}")

if not st.session_state.challenge_data.empty:
    with st.expander("Recent Runs", expanded=False):
        df_display = st.session_state.challenge_data.copy()
        if "date" not in df_display.columns and len(df_display.columns) >= 2:
            df_display.columns = ["date", "distance_km"] + list(df_display.columns[2:])
        if "date" in df_display.columns:
            df_display["date"] = pd.to_datetime(df_display["date"], errors="coerce")
            df_display = df_display.sort_values("date", ascending=False)
            df_display = df_display.drop(columns=["date"])
        st.dataframe(df_display, use_container_width=True)

st.markdown("### Your Badges")

BADGE_IMAGES = {
    "Atlantic Explorer": "images/badges/atlantic_explorer.svg",
    "Eastern Adventurer": "images/badges/eastern_adventurer.svg",
    "Central Challenger": "images/badges/central_challenger.svg",
    "Prairie Voyager": "images/badges/prairie_voyager.svg",
    "True North Finisher": "images/badges/true_north_finisher.svg"
}


def load_badge_image(badge_name, is_earned=True):
    try:
        if badge_name in BADGE_IMAGES:
            with open(BADGE_IMAGES[badge_name], "r") as f:
                svg_content = f.read()
            import re
            svg_content = re.sub(r"<style.*?</style>", "", svg_content, flags=re.DOTALL)
            svg_content = svg_content.replace('class="cls-3"', 'style="fill: #6c1b14;"')
            svg_content = svg_content.replace('class="cls-4"', 'style="fill: #c83d2d;"')
            svg_content = svg_content.replace('class="cls-5"', 'style="fill: #b6291b;"')
            svg_content = svg_content.replace('class="cls-7"', 'style="fill: #fff;"')
            svg_content = svg_content.replace('class="cls-8"', 'style="fill: #b6291b;"')
            svg_content = svg_content.replace('class="cls-6"', 'style="fill: none; stroke: #23262e; stroke-dasharray: .89 .89 .89 .89 .89 .89; stroke-miterlimit: 10; stroke-width: .89px;"')
            svg_content = svg_content.replace('class="cls-2"', 'style="font-family: Montserrat-SemiBoldItalic, \'Montserrat SemiBoldItalic\'; font-size: 11.06px; font-style: italic; font-weight: 600; letter-spacing: .1em;"')
            if not is_earned:
                svg_content = svg_content.replace("<svg", '<svg style="filter: grayscale(100%); opacity: 0.5;"')
            svg_content = svg_content.replace("<svg", '<svg width="150" height="150"')
            st.markdown(svg_content, unsafe_allow_html=True)
        else:
            st.markdown("🏆" if is_earned else "🔒")
    except FileNotFoundError:
        st.markdown("🏆" if is_earned else "🔒")


earned_badges = []
locked_badges = []
for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
    tier_completed = total_logged >= tier_info["total_km"]
    if "badge" in tier_info["checkpoints"][-1]:
        badge_name = tier_info["checkpoints"][-1]["badge"]
        if tier_completed:
            earned_badges.append({"name": badge_name, "challenge": tier_name, "km": tier_info["total_km"], "route": tier_info["route"]})
        else:
            locked_badges.append({"name": badge_name, "challenge": tier_name, "km": tier_info["total_km"], "route": tier_info["route"]})

if earned_badges:
    cols = st.columns(len(earned_badges))
    for i, badge in enumerate(earned_badges):
        with cols[i]:
            load_badge_image(badge["name"], is_earned=True)
else:
    st.info("Complete challenges to earn badges!")

st.markdown("### Challenge Progress")
for tier_name, tier_info in CHALLENGE_CHECKPOINTS.items():
    tier_completed = total_logged >= tier_info["total_km"]
    if tier_completed:
        if "badge" in tier_info["checkpoints"][-1]:
            status_text = f"✅ **{tier_name} {tier_info['total_km']:,} km** | 🍁 {tier_info['checkpoints'][-1]['badge']}"
        else:
            status_text = f"✅ **{tier_name} {tier_info['total_km']:,} km**"
    else:
        status_text = f"⏳ **{tier_name} {tier_info['total_km']:,} km**"

    with st.expander(status_text, expanded=False):
        st.markdown(f"**Route:** {tier_info['route']}")
        st.markdown("**Checkpoints:**")
        for i, checkpoint in enumerate(tier_info["checkpoints"]):
            checkpoint_reached = total_logged >= checkpoint["km"]
            remaining_to_tier = tier_info["total_km"] - checkpoint["km"]
            if "badge" in checkpoint:
                st.markdown(f"✅ {checkpoint['km']:,} km – {checkpoint['location']}" if checkpoint_reached else f"⏳ {checkpoint['km']:,} km – {checkpoint['location']}")
            else:
                st.markdown(f"✅ {checkpoint['km']:,} km – {checkpoint['location']} | {remaining_to_tier:,} km to go" if checkpoint_reached else f"⏳ {checkpoint['km']:,} km – {checkpoint['location']} | {remaining_to_tier:,} km to go")
            if i < len(tier_info["checkpoints"]) - 1:
                st.markdown("")

if total_logged >= 7800:
    st.balloons()
    st.success("Congratulations! You've completed The Great Canadian 7,800K!")
    st.markdown("### Coast-to-Coast Finisher!")
    st.write("You've successfully journeyed from St. John's to Victoria across Canada!")
