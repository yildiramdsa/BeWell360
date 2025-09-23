import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime, timedelta
import plotly.express as px

# ---------------- Constants ----------------
DATA_LINE_COLOR = "#028283"
TARGET_LINE_COLOR = "#e7541e"
TARGET_SLEEP_HRS = 7

# ---------------- Google Sheets Setup ----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)
ws = client.open("sleep_schedule").sheet1

# ---------------- Load Data ----------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(ws.get_all_records())

st.title("🧸 Sleep Schedule")

today = date.today()
default_start = time(22, 0)
default_end = time(6, 0)

# ---------------- Helper Functions ----------------
def calc_duration(row):
    start_dt = datetime.combine(row["date"], row["sleep_start"])
    end_dt = datetime.combine(row["date"], row["sleep_end"])
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return round((end_dt - start_dt).total_seconds() / 3600, 2)

def average_time(times):
    seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in times]
    avg_seconds = sum(seconds) / len(seconds)
    h = int(avg_seconds // 3600) % 24
    m = int((avg_seconds % 3600) // 60)
    return time(h, m)

def get_existing_record(entry_date):
    df = st.session_state.df
    row = df[df["date"] == str(entry_date)]
    if not row.empty:
        idx = row.index[0] + 2  # Google Sheets row (account header)
        return idx, row.iloc[0]
    return None, None

# ---------------- Sleep Entry Form ----------------
entry_date = st.date_input("Date", today)
existing_row_idx, existing_row = get_existing_record(entry_date)

prefill_start = datetime.strptime(existing_row["sleep_start"], "%H:%M").time() if existing_row is not None else default_start
prefill_end = datetime.strptime(existing_row["sleep_end"], "%H:%M").time() if existing_row is not None else default_end

col1, col2 = st.columns(2)
sleep_start = col1.time_input("Sleep Start", prefill_start)
sleep_end = col2.time_input("Sleep End", prefill_end)

# ---------------- Action Buttons ----------------
col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

# ---------------- Handle Save/Delete ----------------
if save_clicked:
    start_str, end_str = sleep_start.strftime("%H:%M"), sleep_end.strftime("%H:%M")
    if existing_row_idx:
        ws.update(values=[[start_str, end_str]], range_name=f"B{existing_row_idx}:C{existing_row_idx}")
        st.success(f"☁️ Updated sleep log for {entry_date}")
    else:
        ws.append_row([str(entry_date), start_str, end_str])
        st.success(f"☁️ Added new sleep log for {entry_date}")
    st.session_state.df = pd.DataFrame(ws.get_all_records())

if delete_clicked and existing_row_idx:
    ws.delete_rows(existing_row_idx)
    st.success(f"🗑️ Deleted sleep log for {entry_date}")
    st.session_state.df = pd.DataFrame(ws.get_all_records())

# ---------------- Analytics ----------------
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["sleep_start"] = pd.to_datetime(df["sleep_start"], format="%H:%M").dt.time
    df["sleep_end"] = pd.to_datetime(df["sleep_end"], format="%H:%M").dt.time
    df["Sleep Duration (hrs)"] = df.apply(calc_duration, axis=1)

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    start_filter = col1.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date, key="start_filter")
    end_filter = col2.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date, key="end_filter")

    filtered_df = pd.DataFrame()
    if start_filter > end_filter:
        st.warning("⚠️ Invalid date range: Start Date cannot be after End Date.")
    else:
        filtered_df = df[(df["date"].dt.date >= start_filter) & (df["date"].dt.date <= end_filter)].copy()

    if not filtered_df.empty:
        avg_start = average_time(filtered_df["sleep_start"])
        avg_end = average_time(filtered_df["sleep_end"])
        avg_duration = filtered_df["Sleep Duration (hrs)"].mean()

        col3.metric("Avg. Sleep Start", avg_start.strftime("%H:%M"))
        col4.metric("Avg. Sleep End", avg_end.strftime("%H:%M"))
        col5.metric("Avg. Sleep Duration (hrs)", f"{avg_duration:.2f}")

        # Line Chart
        duration_chart = filtered_df[["date", "Sleep Duration (hrs)"]].sort_values("date")
        fig = px.line(duration_chart, x="date", y="Sleep Duration (hrs)", markers=True, color_discrete_sequence=[DATA_LINE_COLOR])
        fig.add_hline(y=TARGET_SLEEP_HRS, line_dash="dash", line_color=TARGET_LINE_COLOR,
                      annotation_text=f"Target Sleep ({TARGET_SLEEP_HRS} hrs)", annotation_position="top left")
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Sleep Duration (hrs)",
            xaxis=dict(tickformat="%d %b", tickangle=0, showgrid=False, showline=False),
            yaxis=dict(range=[duration_chart["Sleep Duration (hrs)"].min() - 0.5,
                              duration_chart["Sleep Duration (hrs)"].max() + 0.5],
                       showgrid=False),
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Interactive Table
        df_display = filtered_df.rename(columns={"date": "Date", "sleep_start": "Sleep Start", "sleep_end": "Sleep End"})
        df_display["Date"] = df_display["Date"].dt.date
        df_display["Sleep Start"] = df_display["Sleep Start"].apply(lambda t: t.strftime("%H:%M"))
        df_display["Sleep End"] = df_display["Sleep End"].apply(lambda t: t.strftime("%H:%M"))
        st.dataframe(df_display.sort_values("Date", ascending=False), width='stretch')
else:
    st.info("No sleep logs yet.")