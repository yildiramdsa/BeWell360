import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import base64

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")
with open("images/BeWell360-lg.svg", "rb") as f:
    svg_bytes = f.read()
    encoded_svg = base64.b64encode(svg_bytes).decode()
st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/svg+xml;base64,{encoded_svg}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- Daily Log Pages ----------------
nutrition_and_hydration = st.Page(
    "daily_log_pages/nutrition_and_hydration.py",
    title="Nutrition & Hydration",
    icon="🍎"
)

fitness_activities = st.Page(
    "daily_log_pages/fitness_activities.py",
    title="Fitness Activities",
    icon="⚽"
)

sleep_schedule = st.Page(
    "daily_log_pages/sleep_schedule.py",
    title="Sleep Schedule",
    icon="🧸"
)

body_composition = st.Page(
    "daily_log_pages/body_composition.py",
    title="Body Composition",
    icon="💪"
)

professional_development = st.Page(
    "daily_log_pages/professional_development.py",
    title="Professional Development",
    icon="📚"
)

personal_growth = st.Page(
    "daily_log_pages/personal_growth.py",
    title="Personal Growth",
    icon="🌱"
)

# ---------------- Insights Pages ----------------
dashboard = st.Page(
    "insights_pages/dashboard.py",
    title="Dashboard",
    icon="📌"
)

progress = st.Page(
    "insights_pages/progress.py",
    title="Progress",
    icon="🗓"
)

raw_data = st.Page(
    "insights_pages/raw_data.py",
    title="Raw Data",
    icon="🔍"
)

# ---------------- Life Mastery Planner Pages ----------------
empowering_morning_routine = st.Page(
    "life_mastery_planner_pages/empowering_morning_routine.py",
    title="Empowering Morning Routine",
    icon="☀️"
)

empowering_evening_routine = st.Page(
    "life_mastery_planner_pages/empowering_evening_routine.py",
    title="Empowering Evening Routine",
    icon="🌙"
)

vision_board = st.Page(
    "life_mastery_planner_pages/vision_board.py",
    title="Vision Board",
    icon="🎨"
)

# ---------------- Sidebar Navigation ----------------
pg = st.navigation(
    {
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
)

# ---------------- Data Folder ----------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------- Footer ----------------
st.markdown("<hr>", unsafe_allow_html=True)
with open("images/Oranlytix-lg.svg", "rb") as f:
    svg_bytes = f.read()
    encoded_svg = base64.b64encode(svg_bytes).decode()
footer_html = f"""
<div style="text-align:center;">
    <span style="font-size:10px; color:gray;">Powered by</span>
    <img src="data:image/svg+xml;base64,{encoded_svg}" width="75">
    <div style="font-size:10px; color:gray;">© 2025 BeWell360. All rights reserved.</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)