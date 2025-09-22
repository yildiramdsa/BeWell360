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

try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
except Exception as e:
    st.error("❌ Google Sheets authentication failed.")
    st.text(str(e))
    st.stop()

SHEET_NAME = "sleep_schedule"

# Open spreadsheet and use first tab
try:
    sh = client.open(SHEET_NAME)
    ws = sh.get_worksheet(0)  # first tab
except Exception as e:
    st.error(f"❌ Unable to open spreadsheet '{SHEET_NAME}' or its first tab")
    st.text(str(e))
    st.stop()

# ---------------- Load Existing Data ----------------
@st.cache_data(ttl=60)
def load_sleep_data():
    try:
        records = ws.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error("❌ Failed to load data from Google Sheets.")
        st.text(str(e))
        return pd.DataFrame()

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
        start_str = sleep_start.strftime("%H:%M")
        end_str = sleep_end.strftime("%H:%M")

        try:
            existing_row = None
            for i, row in enumerate(df.to_dict(orient="records"), start=2):
                if str(row.get("date")) == str(entry_date):
                    existing_row = i
                    break

            if existing_row:
                # Update both cells at once using a 2D list
                ws.update(f"B{existing_row}:C{existing_row}", [[start_str, end_str]])
                st.success(f"✅ Updated sleep log for {entry_date}")
            else:
                ws.append_row([str(entry_date), start_str, end_str])
                st.success(f"✅ Added new sleep log for {entry_date}")

            df = load_sleep_data()  # reload dataframe after changes
        except Exception as e:
            st.error("❌ Failed to update Google Sheet.")
            st.text(str(e))

# ---------------- Display Table ----------------
if not df.empty:
    try:
        df["date"] = pd.to_datetime(df["date"]).dt.date
        st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))
    except Exception as e:
        st.error("❌ Failed to display data table.")
        st.text(str(e))
else:
    st.info("No sleep logs yet. Add your first one above ⬆️")