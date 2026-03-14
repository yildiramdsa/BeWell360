import os
import base64
import streamlit as st

DATA_DIR = "data"
HEADER_SVG = "images/BeWell360-lg.svg"
FOOTER_SVG = "images/SnowyOwlDataTextLogo.svg"

st.set_page_config(page_title="BeWell360", layout="wide")


def load_svg(file_path):
    """Load an SVG and encode it as base64. Returns None if file is missing or unreadable."""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (FileNotFoundError, OSError):
        return None

def create_pages(page_list):
    """Create a list of st.Page objects from a list of tuples (path, title, icon)."""
    return [st.Page(path, title=title, icon=icon) for path, title, icon in page_list]


header_b64 = load_svg(HEADER_SVG)
if header_b64:
    st.markdown(
        f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{header_b64}" width="250"></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div style="text-align:center; font-size:1.5rem; font-weight:bold;">BeWell360</div>', unsafe_allow_html=True)

daily_log_pages = create_pages([
    ("nutrition_and_hydration.py", "Nutrition & Hydration", "🍎"),
    ("fitness_activities.py", "Fitness Activities", "⚽"),
    ("sleep_schedule.py", "Sleep Schedule", "🧸"),
    ("professional_and_personal_development.py", "Professional & Personal Development", "📚"),
    ("daily_routine.py", "Routines", "⭐"),
])

ai_pages = create_pages([
    ("progress_dashboard.py", "Progress", "📊"),
    ("daily_ai_summary.py", "Daily Summary", "🦉"),
    ("ai_chat_coach.py", "Coach Chat", "💬"),
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

pages = {
    "Daily Log": daily_log_pages,
    "Insights & Coach": ai_pages,
    "Goals & Vision": goals_pages,
    "Challenges": challenges_pages,
}

nav = st.navigation(pages)
nav.run()

os.makedirs(DATA_DIR, exist_ok=True)

footer_b64 = load_svg(FOOTER_SVG)
footer_img = f'<img src="data:image/svg+xml;base64,{footer_b64}" width="150">' if footer_b64 else ""
st.markdown(
    f'<div style="text-align:center;"><span style="font-size:12px; color:gray;">Powered by</span> {footer_img} <div style="font-size:12px; color:gray;">© 2026 BeWell360. All rights reserved.</div></div>',
    unsafe_allow_html=True,
)