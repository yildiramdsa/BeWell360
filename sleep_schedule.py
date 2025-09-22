import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime, timedelta

# ---------------- Google Sheets Setup ----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)

SHEET_NAME = "sleep_schedule"
ws = client.open(SHEET_NAME).sheet1  # first worksheet

# ---------------- Load or initialize data ----------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(ws.get_all_records())

# ---------------- Form ----------------
st.title("🧸 Sleep Schedule")

today = date.today()
default_start = time(22, 0)
default_end = time(6, 0)

with st.form("sleep_form", clear_on_submit=False):
    entry_date = st.date_input("Date", today)
    
    col1, col2 = st.columns(2)
    sleep_start = col1.time_input("Sleep Start", default_start)
    sleep_end = col2.time_input("Sleep End", default_end)

    if st.form_submit_button("☁️ Save"):
        start_str, end_str = sleep_start.strftime("%H:%M"), sleep_end.strftime("%H:%M")

        # Check if entry exists
        df_records = st.session_state.df.to_dict(orient="records")
        existing_row_idx = next(
            (i + 2 for i, row in enumerate(df_records) if str(row.get("date")) == str(entry_date)),
            None
        )

        if existing_row_idx:
            ws.update(values=[[start_str, end_str]], range_name=f"B{existing_row_idx}:C{existing_row_idx}")
            st.success(f"✅ Updated sleep log for {entry_date}")
        else:
            ws.append_row([str(entry_date), start_str, end_str])
            st.success(f"✅ Added new sleep log for {entry_date}")

        st.session_state.df = pd.DataFrame(ws.get_all_records())

# ---------------- Display Table and Analytics ----------------
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    
    # Convert columns
    df["date"] = pd.to_datetime(df["date"])
    df["sleep_start"] = pd.to_datetime(df["sleep_start"], format="%H:%M").dt.time
    df["sleep_end"] = pd.to_datetime(df["sleep_end"], format="%H:%M").dt.time

    # Compute sleep duration in hours
    def calc_duration(row):
        start_dt = datetime.combine(row["date"], row["sleep_start"])
        end_dt = datetime.combine(row["date"], row["sleep_end"])
        if end_dt <= start_dt:  # handle overnight sleep
            end_dt += timedelta(days=1)
        return (end_dt - start_dt).total_seconds() / 3600

    df["Sleep Duration (hrs)"] = df.apply(calc_duration, axis=1)

    # Helper to compute average time correctly
    def average_time(times):
        seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in times]
        avg_seconds = sum(seconds) / len(seconds)
        h = int(avg_seconds // 3600) % 24
        m = int((avg_seconds % 3600) // 60)
        return time(h, m)

    avg_sleep_start = average_time(df["sleep_start"])
    avg_sleep_end = average_time(df["sleep_end"])

    # ---------------- Metrics / Cards ----------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Sleep Duration (hrs)", f"{df['Sleep Duration (hrs)'].mean():.2f}")
    col2.metric("Average Sleep Start", avg_sleep_start.strftime("%H:%M"))
    col3.metric("Average Sleep End", avg_sleep_end.strftime("%H:%M"))

    # ---------------- Table ----------------
    df_display = df.rename(columns={
        "date": "Date",
        "sleep_start": "Sleep Start",
        "sleep_end": "Sleep End"
    }).reset_index(drop=True)

    st.dataframe(df_display.sort_values("Date", ascending=False), width='stretch')

    # ---------------- Line Chart ----------------
    duration_chart = df_display[["Date", "Sleep Duration (hrs)"]].set_index("Date").sort_index()
    st.line_chart(duration_chart)
else:
    st.info("No sleep logs yet.")