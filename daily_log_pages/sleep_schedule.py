import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ---------------- Setup ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "sleep_schedule.csv")

# Load existing data if file exists
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE, parse_dates=["date"])
else:
    df = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])

# ---------------- Form ----------------
st.header("🛌 Sleep Schedule")

# Default values
today = date.today()
selected_date = st.date_input("Date", today)

# Check if entry already exists
existing_entry = df[df["date"] == pd.to_datetime(selected_date)]

if not existing_entry.empty:
    sleep_start_default = existing_entry.iloc[0]["sleep_start"]
    sleep_end_default = existing_entry.iloc[0]["sleep_end"]
else:
    sleep_start_default = ""
    sleep_end_default = ""

with st.form("sleep_form"):
    sleep_start = st.text_input("Sleep Start (e.g., 22:30)", value=sleep_start_default)
    sleep_end = st.text_input("Sleep End (e.g., 06:30)", value=sleep_end_default)
    submitted = st.form_submit_button("Save")

if submitted:
    # Remove old entry for this date if exists
    df = df[df["date"] != pd.to_datetime(selected_date)]

    # Add new/updated row
    new_row = {
        "date": pd.to_datetime(selected_date),
        "sleep_start": sleep_start,
        "sleep_end": sleep_end,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save back to CSV
    df.to_csv(CSV_FILE, index=False)

    st.success(f"Sleep schedule saved for {selected_date.strftime('%Y-%m-%d')} ✅")

# ---------------- Display Table ----------------
if not df.empty:
    st.subheader("Your Sleep History")
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))