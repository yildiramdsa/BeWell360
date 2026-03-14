import streamlit as st
import os
import base64

# ---------------- Constants ----------------
DATA_DIR = "data"
HEADER_SVG = "images/BeWell360-lg.svg"
FOOTER_SVG = "images/SnowyOwlDataTextLogo.svg"

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")

# ---------------- Helpers ----------------
def load_svg(file_path):
    """Load an SVG and encode it as base64."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def create_pages(page_list):
    """Create a list of st.Page objects from a list of tuples (path, title, icon)."""
    return [st.Page(path, title=title, icon=icon) for path, title, icon in page_list]

# ---------------- Header ----------------
st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/svg+xml;base64,{load_svg(HEADER_SVG)}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- Pages ----------------
daily_log_pages = create_pages([
    ("nutrition_and_hydration.py", "Nutrition & Hydration", "🍎"),
    ("fitness_activities.py", "Fitness Activities", "⚽"),
    ("sleep_schedule.py", "Sleep Schedule", "🧸"),
    ("professional_and_personal_development.py", "Professional & Personal Development", "📚"),
])

ai_pages = create_pages([
    ("daily_ai_summary.py", "Daily AI Insights", "🦉"),
    ("ai_chat_coach.py", "AI Coach Chat", "💬"),
])

life_mastery_pages = create_pages([
    ("empowering_morning_routine.py", "Empowering Morning Routine", "☀️"),
    ("empowering_evening_routine.py", "Empowering Evening Routine", "🌙"),
    ("daily_empowering_habits.py", "Daily Empowering Habits", "⭐"),
])

goals_pages = create_pages([
    ("goals_for_the_year.py", "Annual Goals", "🎯"),
    ("long_term_life_goals.py", "Long-Term Goals", "📌"),
    ("vision_board.py", "Vision Board", "🎨"),
])

challenges_pages = create_pages([
    ("the_great_canadian_7800k.py", "The Great Canadian 7,800K", "🍁"),
    ("the_yukon_63k.py", "The Yukon 63K", "❄️"),
])

progress_pages = create_pages([
    ("progress_dashboard.py", "Progress Dashboard", "📊"),
    ("habit_consistency.py", "Habit Consistency", "📅"),
    ("health_trends.py", "Health Trends", "📈"),
])

pages = {
    "Daily Log": daily_log_pages,
    "Life Mastery Planner": life_mastery_pages,
    "AI Coach": ai_pages,
    "Goals": goals_pages,
    "Challenges": challenges_pages,
    "Progress & Analytics": progress_pages,
}
# ---------------- Navigation ----------------
pg = st.navigation(pages)
pg.run()  # Execute the selected page

# ---------------- Data Folder ----------------
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- Footer ----------------
footer_html = f"""
<div style="text-align:center;">
    <span style="font-size:12px; color:gray;">Powered by</span>
    <img src="data:image/svg+xml;base64,{load_svg(FOOTER_SVG)}" width="150">
    <div style="font-size:12px; color:gray;">© 2026 BeWell360. All rights reserved.</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)