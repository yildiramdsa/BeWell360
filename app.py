import streamlit as st
import os
import base64

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")

# Helper to load SVGs
def load_svg(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ---------------- Header ----------------
st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/svg+xml;base64,{load_svg('images/BeWell360-lg.svg')}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- Daily Log Pages ----------------
nutrition_and_hydration = st.Page("nutrition_and_hydration.py", title="Nutrition & Hydration", icon="🍎")
fitness_activities = st.Page("fitness_activities.py", title="Fitness Activities", icon="⚽")
sleep_schedule = st.Page("sleep_schedule.py", title="Sleep Schedule", icon="🧸")
body_composition = st.Page("body_composition.py", title="Body Composition", icon="💪")
professional_development = st.Page("professional_development.py", title="Professional Development", icon="📚")
personal_growth = st.Page("personal_growth.py", title="Personal Growth", icon="🌱")

# ---------------- Insights Pages ----------------
dashboard = st.Page("dashboard.py", title="Dashboard", icon="📌")
progress = st.Page("progress.py", title="Progress", icon="🗓")
raw_data = st.Page("raw_data.py", title="Raw Data", icon="🔍")

# ---------------- Life Mastery Planner Pages ----------------
empowering_morning_routine = st.Page("empowering_morning_routine.py", title="Empowering Morning Routine", icon="☀️")
empowering_evening_routine = st.Page("empowering_evening_routine.py", title="Empowering Evening Routine", icon="🌙")
vision_board = st.Page("vision_board.py", title="Vision Board", icon="🎨")

# ---------------- Sidebar Navigation ----------------
pages = {
    "Daily Log": [
        nutrition_and_hydration,
        fitness_activities,
        sleep_schedule,
        body_composition,
        professional_development,
        personal_growth,
    ],
    "Insights": [
        dashboard,
        progress,
        raw_data,
    ],
    "Life Mastery Planner": [
        empowering_morning_routine,
        empowering_evening_routine,
        vision_board,
    ]
}

pg = st.navigation(pages)
pg.run()  # <-- execute the selected page

# ---------------- Data Folder ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- Footer ----------------
st.markdown("<hr>", unsafe_allow_html=True)
footer_html = f"""
<div style="text-align:center;">
    <span style="font-size:10px; color:gray;">Powered by</span>
    <img src="data:image/svg+xml;base64,{load_svg('images/Oranlytix-lg.svg')}" width="75">
    <div style="font-size:10px; color:gray;">© 2025 BeWell360. All rights reserved.</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)