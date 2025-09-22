import streamlit as st
import pandas as pd
import os
from datetime import date, time

# ---------------- Setup ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "sleep_schedule.csv")

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE, parse_dates=["date"])
else:
    df = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])

# ---------------- Form ----------------
st.header("🛌 Sleep Schedule")

today = date.today()
selected_date = st.date_input("Date", today)

# Check if this date already has data
existing_entry = df[df["date"] == pd.to_datetime(selected_date)]

if not existing_entry.empty:
    # Convert stored strings back to time objects if possible
    try:
        sleep_start_default = pd.to_datetime(existing_entry.iloc[0]["sleep_start"]).time()
    except Exception:
        sleep_start_default = time(22, 0)  # default 10:00 PM
    try:
        sleep_end_default = pd.to_datetime(existing_entry.iloc[0]["sleep_end"]).time()
    except Exception:
        sleep_end_default = time(6, 0)  # default 6:00 AM
else:
    sleep_start_default = time(22, 0)
    sleep_end_default = time(6, 0)

with st.form("sleep_form"):
    sleep_start = st.time_input("Sleep Start", value=sleep_start_default)
    sleep_end = st.time_input("Sleep End", value=sleep_end_default)
    submitted = st.form_submit_button("Save")

if submitted:
    # Remove old entry if exists
    df = df[df["date"] != pd.to_datetime(selected_date)]

    # Add new row
    new_row = {
        "date": pd.to_datetime(selected_date),
        "sleep_start": sleep_start.strftime("%H:%M"),
        "sleep_end": sleep_end.strftime("%H:%M"),
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save
    df.to_csv(CSV_FILE, index=False)
    st.success(f"✅ Saved sleep schedule for {selected_date}")

# ---------------- Table ----------------
if not df.empty:
    st.subheader("Your Sleep History")
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))