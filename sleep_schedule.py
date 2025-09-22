import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime, timedelta
import plotly.express as px

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

    # ---------------- Date Range Filter ----------------
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.date_input(
        "Filter by Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    start_filter, end_filter = date_range
    filtered_df = df[(df["date"].dt.date >= start_filter) & (df["date"].dt.date <= end_filter)].copy()

    # ---------------- Metrics / Cards ----------------
    if not filtered_df.empty:
        avg_sleep_start = average_time(filtered_df["sleep_start"])
        avg_sleep_end = average_time(filtered_df["sleep_end"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Average Sleep Duration (hrs)", f"{filtered_df['Sleep Duration (hrs)'].mean():.2f}")
        col2.metric("Average Sleep Start", avg_sleep_start.strftime("%H:%M"))
        col3.metric("Average Sleep End", avg_sleep_end.strftime("%H:%M"))

        # ---------------- Table ----------------
        df_display = filtered_df.rename(columns={
            "date": "Date",
            "sleep_start": "Sleep Start",
            "sleep_end": "Sleep End"
        }).reset_index(drop=True)

        st.dataframe(df_display.sort_values("Date", ascending=False), width='stretch')

        # ---------------- Improved Line Chart ----------------
        duration_chart = df_display[["Date", "Sleep Duration (hrs)"]].sort_values("Date")

        fig = px.line(
            duration_chart,
            x="Date",
            y="Sleep Duration (hrs)",
            markers=True,
            title="Sleep Duration Over Time"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Duration (hrs)",
            xaxis=dict(
                tickformat="%d %b",  # day + short month
                tickangle=0  # horizontal labels
            ),
            yaxis=dict(range=[0, max(duration_chart["Sleep Duration (hrs)"].max() + 1, 8)]),
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sleep logs in the selected date range.")
else:
    st.info("No sleep logs yet.")