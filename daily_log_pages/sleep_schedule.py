import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------- Page Config ----------------
st.set_page_config(page_title="Sleep Schedule", layout="wide")
st.title("Sleep Schedule")

# ---------------- Data File ----------------
DATA_DIR = "data"
csv_file = os.path.join(DATA_DIR, "sleep_schedule.csv")
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["date", "sleep_start", "sleep_end"])
    df.to_csv(csv_file, index=False)
else:
    df = pd.read_csv(csv_file)

# ---------------- Form ----------------
with st.form("sleep_form"):
    # Default date today
    date = st.date_input("Date", datetime.today())
    
    # Check if row exists for this date
    existing_row = df[df["date"] == date.strftime("%Y-%m-%d")]
    if not existing_row.empty:
        sleep_start = st.time_input("Sleep Start", datetime.strptime(existing_row.iloc[0]["sleep_start"], "%H:%M").time())
        sleep_end = st.time_input("Sleep End", datetime.strptime(existing_row.iloc[0]["sleep_end"], "%H:%M").time())
    else:
        sleep_start = st.time_input("Sleep Start")
        sleep_end = st.time_input("Sleep End")

    submitted = st.form_submit_button("Save")
    if submitted:
        # Update existing row or add new
        if not existing_row.empty:
            df.loc[df["date"] == date.strftime("%Y-%m-%d"), ["sleep_start", "sleep_end"]] = [sleep_start.strftime("%H:%M"), sleep_end.strftime("%H:%M")]
        else:
            df = pd.concat([df, pd.DataFrame([{
                "date": date.strftime("%Y-%m-%d"),
                "sleep_start": sleep_start.strftime("%H:%M"),
                "sleep_end": sleep_end.strftime("%H:%M")
            }])], ignore_index=True)

        df.to_csv(csv_file, index=False)
        st.success("Saved successfully!")

# ---------------- Show Table ----------------
st.dataframe(df.sort_values("date", ascending=False))