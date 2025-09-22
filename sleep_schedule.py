import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time

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

sh = client.open(SHEET_NAME)
ws = sh.get_worksheet(0)  # use first tab

# ---------------- Load or initialize data ----------------
if "df" not in st.session_state:
    records = ws.get_all_records()
    st.session_state.df = pd.DataFrame(records)

# ---------------- Form ----------------
st.title("🧸 Sleep Schedule")

today = date.today()
default_start = time(22, 0)
default_end = time(6, 0)

with st.form("sleep_form", clear_on_submit=False):
    entry_date = st.date_input("Date", today)
    sleep_start = st.time_input("Sleep Start", default_start)
    sleep_end = st.time_input("Sleep End", default_end)

    submitted = st.form_submit_button("☁️ Save")

    if submitted:
        sleep_str = f"{sleep_start.strftime('%H:%M')} - {sleep_end.strftime('%H:%M')}"

        existing_row = None
        for i, row in enumerate(st.session_state.df.to_dict(orient="records"), start=2):
            if str(row.get("date")) == str(entry_date):
                existing_row = i
                break

        if existing_row:
            ws.update(f"B{existing_row}", [[sleep_str]])
            st.success(f"✅ Updated sleep log for {entry_date}")
        else:
            ws.append_row([str(entry_date), sleep_str])
            st.success(f"✅ Added new sleep log for {entry_date}")

        # Reload data after update
        records = ws.get_all_records()
        st.session_state.df = pd.DataFrame(records)

# ---------------- Display Table ----------------
if not st.session_state.df.empty:
    df_display = st.session_state.df.copy()
    df_display["date"] = pd.to_datetime(df_display["date"]).dt.date
    st.dataframe(df_display.sort_values("date", ascending=False), use_container_width=True)
else:
    st.info("No sleep logs yet.")