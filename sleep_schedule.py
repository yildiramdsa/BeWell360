import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time

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
def load_sleep_data():
    records = ws.get_all_records()
    return pd.DataFrame(records)

df = load_sleep_data()

# ---------------- Form ----------------
st.title("🧸 Sleep Schedule")

today = date.today()
default_start = time(22, 0)  # 22:00
default_end = time(6, 0)     # 06:00

with st.form("sleep_form", clear_on_submit=False):
    entry_date = st.date_input("Date", today)
    sleep_start = st.time_input("Sleep Start", default_start)
    sleep_end = st.time_input("Sleep End", default_end)

    submitted = st.form_submit_button("💾 Save")

    if submitted:
        # Check if date already exists in sheet
        records = ws.get_all_records()
        existing_row = None
        for i, row in enumerate(records, start=2):  # row 1 is headers
            if str(row["date"]) == str(entry_date):
                existing_row = i
                break

        start_str = sleep_start.strftime("%H:%M")
        end_str = sleep_end.strftime("%H:%M")

        if existing_row:
            ws.update(f"B{existing_row}", start_str)
            ws.update(f"C{existing_row}", end_str)
            st.success(f"✅ Updated sleep log for {entry_date}")
        else:
            ws.append_row([str(entry_date), start_str, end_str])
            st.success(f"✅ Added new sleep log for {entry_date}")

        df = load_sleep_data()  # reload dataframe after changes

# ---------------- Display Table ----------------
if not df.empty:
    df["date"] = pd.to_datetime(df["date"]).dt.date
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))
else:
    st.info("No sleep logs yet. Add your first one above ⬆️")