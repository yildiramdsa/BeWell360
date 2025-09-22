import streamlit as st
import pandas as pd
from datetime import datetime, time
import os

# ---------------- Data Folder ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
SLEEP_CSV = os.path.join(DATA_DIR, "sleep_schedule.csv")

# Ensure CSV exists
if not os.path.exists(SLEEP_CSV):
    df_init = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])
    df_init.to_csv(SLEEP_CSV, index=False)

# Load CSV
df = pd.read_csv(SLEEP_CSV, parse_dates=["date"])

st.title("🧸 Sleep Schedule")

# ---------------- Form ----------------
with st.form("sleep_form", clear_on_submit=False):
    # Select date (default today)
    today = datetime.today().date()
    selected_date = st.date_input("Date", value=today)

    # Check if date already exists in CSV
    existing_row = df[df["date"] == pd.Timestamp(selected_date)]
    if not existing_row.empty:
        default_start = pd.to_datetime(existing_row.iloc[0]["sleep_start"]).time()
        default_end = pd.to_datetime(existing_row.iloc[0]["sleep_end"]).time()
    else:
        default_start = time(22, 0)  # default 10 PM
        default_end = time(6, 0)     # default 6 AM

    sleep_start = st.time_input("Sleep Start", value=default_start)
    sleep_end = st.time_input("Sleep End", value=default_end)

    submitted = st.form_submit_button("Save")

    if submitted:
        # Prepare row
        new_row = {
            "date": selected_date,
            "sleep_start": sleep_start.strftime("%H:%M"),
            "sleep_end": sleep_end.strftime("%H:%M"),
        }

        # Update existing row or append
        if not existing_row.empty:
            df.loc[df["date"] == pd.Timestamp(selected_date), ["sleep_start", "sleep_end"]] = [
                new_row["sleep_start"],
                new_row["sleep_end"],
            ]
            st.success(f"Updated sleep schedule for {selected_date}")
        else:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Added sleep schedule for {selected_date}")

        # Save CSV
        df.to_csv(SLEEP_CSV, index=False)

# ---------------- Display Data ----------------
st.subheader("Recent Sleep Logs")
st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))