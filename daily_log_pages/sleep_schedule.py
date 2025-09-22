import streamlit as st
import pandas as pd
import os
from datetime import datetime, time

# Path for sleep log data
DATA_FILE = "data/sleep_schedule.csv"

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

# Load data if file exists
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
else:
    df = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])

st.title("😴 Sleep Schedule")

# Form
with st.form("sleep_form"):
    today = datetime.today().date()
    selected_date = st.date_input("Date", value=today)

    # If date already exists, load values
    existing = df[df["date"] == pd.to_datetime(selected_date)]
    if not existing.empty:
        default_start = datetime.strptime(existing.iloc[0]["sleep_start"], "%H:%M:%S").time()
        default_end = datetime.strptime(existing.iloc[0]["sleep_end"], "%H:%M:%S").time()
    else:
        default_start = time(23, 0)
        default_end = time(7, 0)

    sleep_start = st.time_input("Sleep Start", value=default_start)
    sleep_end = st.time_input("Sleep End", value=default_end)

    submitted = st.form_submit_button("💾 Save")

    if submitted:
        # Remove old entry for that date if exists
        df = df[df["date"] != pd.to_datetime(selected_date)]

        # Add new/updated entry
        new_row = pd.DataFrame([{
            "date": selected_date,
            "sleep_start": sleep_start.strftime("%H:%M:%S"),
            "sleep_end": sleep_end.strftime("%H:%M:%S")
        }])
        df = pd.concat([df, new_row], ignore_index=True)

        # Save to CSV
        df.to_csv(DATA_FILE, index=False)
        st.success(f"Sleep data saved for {selected_date} ✅")

# Show data table
if not df.empty:
    st.subheader("Your Sleep History")
    st.dataframe(df.sort_values("date", ascending=False))