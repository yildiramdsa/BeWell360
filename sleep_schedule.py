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
            # ✅ Updated gspread syntax with named arguments
            ws.update(values=[[start_str, end_str]], range_name=f"B{existing_row_idx}:C{existing_row_idx}")
            st.success(f"✅ Updated sleep log for {entry_date}")
        else:
            ws.append_row([str(entry_date), start_str, end_str])
            st.success(f"✅ Added new sleep log for {entry_date}")

        # Reload updated data
        st.session_state.df = pd.DataFrame(ws.get_all_records())

# ---------------- Display Table ----------------
if not st.session_state.df.empty:
    df_display = st.session_state.df.copy()
    df_display["date"] = pd.to_datetime(df_display["date"]).dt.date
    st.dataframe(df_display.sort_values("date", ascending=False), width='stretch')
else:
    st.info("No sleep logs yet.")