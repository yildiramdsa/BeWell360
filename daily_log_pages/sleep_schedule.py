import streamlit as st
import pandas as pd
from datetime import datetime, time
import os

# ---------------- Data Setup ----------------
DATA_DIR = "data"
SLEEP_FILE = os.path.join(DATA_DIR, "sleep_schedule.csv")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# If file doesn’t exist, create with headers
if not os.path.exists(SLEEP_FILE):
    df = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])
    df.to_csv(SLEEP_FILE, index=False)

# ---------------- Load Data ----------------
df = pd.read_csv(SLEEP_FILE)

# Ensure date column is string for easy comparison
df["date"] = df["date"].astype(str)

# ---------------- Form ----------------
st.title("🧸 Sleep Schedule")

# Default to today
selected_date = st.date_input("Date", datetime.today())

# Convert to string for consistency
selected_date_str = selected_date.strftime("%Y-%m-%d")

# Check if record exists
existing_row = df[df["date"] == selected_date_str]

# Prefill values if available
if not existing_row.empty:
    default_start = datetime.strptime(existing_row.iloc[0]["sleep_start"], "%H:%M").time()
    default_end = datetime.strptime(existing_row.iloc[0]["sleep_end"], "%H:%M").time()
else:
    default_start = time(22, 0)  # 10:00 PM
    default_end = time(6, 0)     # 6:00 AM

with st.form("sleep_form"):
    sleep_start = st.time_input("Sleep Start", value=default_start)
    sleep_end = st.time_input("Sleep End", value=default_end)
    submitted = st.form_submit_button("💾 Save")

if submitted:
    # Update or add row
    if not existing_row.empty:
        df.loc[df["date"] == selected_date_str, ["sleep_start", "sleep_end"]] = [
            sleep_start.strftime("%H:%M"),
            sleep_end.strftime("%H:%M"),
        ]
    else:
        new_row = {
            "date": selected_date_str,
            "sleep_start": sleep_start.strftime("%H:%M"),
            "sleep_end": sleep_end.strftime("%H:%M"),
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(SLEEP_FILE, index=False)
    st.success(f"Sleep schedule for **{selected_date_str}** saved successfully!")