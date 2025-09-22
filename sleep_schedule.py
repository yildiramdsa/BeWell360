import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime

# ---------------- Google Sheets Setup ----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
client = gspread.authorize(creds)

SHEET_NAME = "BeWell360_Data"
WORKSHEET = "Sleep"

# open sheet
sh = client.open(SHEET_NAME)
ws = sh.worksheet(WORKSHEET)

# ---------------- Load Existing Data ----------------
records = ws.get_all_records()
df = pd.DataFrame(records)

# ---------------- Form ----------------
st.title("🧸 Sleep Schedule")

today = date.today()
default_start = time(22, 0)  # 22:00
default_end = time(6, 0)    # 06:00

with st.form("sleep_form", clear_on_submit=False):
    entry_date = st.date_input("Date", today)
    sleep_start = st.time_input("Sleep Start", default_start)
    sleep_end = st.time_input("Sleep End", default_end)

    submitted = st.form_submit_button("💾 Save")

    if submitted:
        # Check if date already exists in sheet
        existing_row = None
        for i, row in enumerate(records, start=2):  # row 1 is headers
            if str(row["date"]) == str(entry_date):
                existing_row = i
                break

        if existing_row:
            # Update existing row
            ws.update(f"B{existing_row}", str(sleep_start))
            ws.update(f"C{existing_row}", str(sleep_end))
            st.success(f"✅ Updated sleep log for {entry_date}")
        else:
            # Append new row
            ws.append_row([str(entry_date), str(sleep_start), str(sleep_end)])
            st.success(f"✅ Added new sleep log for {entry_date}")

# ---------------- Display Table ----------------
if not df.empty:
    df["date"] = pd.to_datetime(df["date"]).dt.date
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))
else:
    st.info("No sleep logs yet. Add your first one above ⬆️")