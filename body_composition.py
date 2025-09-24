import streamlit as st
import pandas as pd
import os
from datetime import date

# ---------------- Constants ----------------
DATA_DIR = "data"
EXCEL_FILE = os.path.join(DATA_DIR, "body_composition.xlsx")

# ---------------- Page Config ----------------
st.set_page_config(page_title="Body Composition", layout="wide")

# ---------------- Helpers ----------------
def load_data():
    """Load existing data or create a new DataFrame."""
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["date", "weight_lb", "body_fat_percent", "skeletal_muscle_percent"])

def save_data(df):
    """Save DataFrame to Excel."""
    df.to_excel(EXCEL_FILE, index=False)

# ---------------- UI ----------------
st.title("💪 Body Composition Tracker")

st.markdown("Track your **weight, body fat %, and skeletal muscle %** over time.")

# Load data
df = load_data()

# Input Form
with st.form("body_composition_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        entry_date = st.date_input("Date", date.today())
    with col2:
        weight = st.number_input("Weight (lb)", min_value=0.0, format="%.1f")
    with col3:
        body_fat = st.number_input("Body Fat (%)", min_value=0.0, max_value=100.0, format="%.1f")
    with col4:
        muscle = st.number_input("Skeletal Muscle (%)", min_value=0.0, max_value=100.0, format="%.1f")

    submitted = st.form_submit_button("Add Entry")
    if submitted:
        new_entry = {"date": entry_date, "weight_lb": weight, "body_fat_percent": body_fat, "skeletal_muscle_percent": muscle}
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(df)
        st.success("✅ Entry added!")

# Show Data
st.subheader("📊 Your Data")
st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

# Charts
if not df.empty:
    st.subheader("📈 Trends Over Time")
    df_sorted = df.sort_values("date")

    st.line_chart(df_sorted.set_index("date")[["weight_lb"]], height=250)
    st.line_chart(df_sorted.set_index("date")[["body_fat_percent", "skeletal_muscle_percent"]], height=250)
