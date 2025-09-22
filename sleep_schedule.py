import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ---------------- Constants ----------------
DATA_DIR = "data"
SLEEP_CSV = os.path.join(DATA_DIR, "sleep_schedule.csv")

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- Load existing data ----------------
if os.path.exists(SLEEP_CSV):
    df = pd.read_csv(SLEEP_CSV)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
else:
    df = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])

st.title("🛌 Sleep Schedule")

# ---------------- Form ----------------
st.subheader("Add / Edit Sleep Entry")

# Default to today
default_date = date.today()

selected_date = st.date_input("Date", value=default_date)

# Check if entry exists
existing_row = df[df["date"] == pd.to_datetime(selected_date)]

if not existing_row.empty:
    sleep_start_default = existing_row.iloc[0]["sleep_start"]
    sleep_end_default = existing_row.iloc[0]["sleep_end"]
else:
    sleep_start_default = ""
    sleep_end_default = ""

with st.form("sleep_form"):
    sleep_start = st.time_input("Sleep Start Time", value=pd.to_datetime(sleep_start_default).time() if sleep_start_default else datetime.now().time())
    sleep_end = st.time_input("Sleep End Time", value=pd.to_datetime(sleep_end_default).time() if sleep_end_default else datetime.now().time())
    submitted = st.form_submit_button("Save Entry")

    if submitted:
        # Remove existing row if present
        df = df[df["date"] != pd.to_datetime(selected_date)]
        # Append new/updated row
        new_row = pd.DataFrame({
            "date": [pd.to_datetime(selected_date)],
            "sleep_start": [sleep_start.strftime("%H:%M")],
            "sleep_end": [sleep_end.strftime("%H:%M")]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(SLEEP_CSV, index=False)
        st.success("Sleep entry saved!")

# ---------------- Display Existing Data ----------------
if not df.empty:
    st.subheader("Recent Sleep Logs")
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))
else:
    st.info("No sleep logs found. Add a new entry above.")