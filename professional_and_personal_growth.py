import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

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
ws = client.open("professional_and_personal_growth").sheet1

# ---------------- Load Data ----------------
if "growth_df" not in st.session_state:
    st.session_state.growth_df = pd.DataFrame(ws.get_all_records())

st.title("🌱 Professional & Personal Growth")

today = date.today()

# ---------------- Entry Form ----------------
entry_date = st.date_input("Date", today)

# Find existing record
df_records = st.session_state.growth_df.to_dict(orient="records")
existing_row_idx, existing_row = None, None
for i, row in enumerate(df_records):
    if str(row.get("date")) == str(entry_date):
        existing_row_idx = i + 2  # account for header row
        existing_row = row
        break

# Prefill values
def find_cols(record: dict):
    prof_key = None
    pers_key = None
    for col in record.keys():
        cl = col.lower()
        if prof_key is None and ("professional" in cl or "dev" in cl):
            prof_key = col
        if pers_key is None and ("personal" in cl or "growth" in cl):
            pers_key = col
    # Fallback order-based if not found
    keys = list(record.keys())
    if prof_key is None and len(keys) > 1:
        prof_key = keys[1]
    if pers_key is None and len(keys) > 2:
        pers_key = keys[2]
    return prof_key, pers_key

if existing_row:
    prof_col, pers_col = find_cols(existing_row)
    prefill_prof = str(existing_row.get(prof_col, "")) if prof_col else ""
    prefill_pers = str(existing_row.get(pers_col, "")) if pers_col else ""
else:
    prefill_prof = ""
    prefill_pers = ""

col1, col2 = st.columns(2)
with col1:
    professional_development = st.text_area(
        "Professional Development",
        value=prefill_prof,
        height=120
    )
with col2:
    personal_growth = st.text_area(
        "Personal Growth",
        value=prefill_pers,
        height=120
    )

# ---------------- Action Buttons ----------------
col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

# ---------------- Handle Save/Delete ----------------
if save_clicked:
    try:
        if existing_row_idx:
            ws.update(values=[[professional_development, personal_growth]], range_name=f"B{existing_row_idx}:C{existing_row_idx}")
            st.success(f"Updated growth log for {entry_date}.")
        else:
            ws.append_row([str(entry_date), professional_development, personal_growth])
            st.success(f"Added new growth log for {entry_date}.")
        st.session_state.growth_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

if delete_clicked and existing_row_idx:
    try:
        ws.delete_rows(existing_row_idx)
        st.success(f"Deleted growth log for {entry_date}.")
        st.session_state.growth_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")

# ---------------- Analytics ----------------
if not st.session_state.growth_df.empty:
    df = st.session_state.growth_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # ---------------- Date Filter (same row) ----------------
    valid_dates = df["date"].dropna()
    if valid_dates.empty:
        st.warning("No valid dates found in the data.")
        st.stop()

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    # Fallback if needed
    today_val = date.today()
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = today_val
        max_date = today_val

    # ---------------- Results Section ----------------
    st.subheader("🔍 Growth Analysis")
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        start_filter = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    with filter_col2:
        end_filter = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

    if start_filter > end_filter:
        st.warning("⚠️ Invalid date range: Start Date cannot be after End Date.")
        filtered_df = pd.DataFrame()
    else:
        filtered_df = df[(df["date"].dt.date >= start_filter) & (df["date"].dt.date <= end_filter)].copy()

    if not filtered_df.empty:
        # ---------------- Interactive Table ----------------
        df_display = filtered_df.rename(columns={
            "date": "Date",
        })

        # Standardize optional column names for display
        def resolve_col(cols, candidates):
            for c in candidates:
                if c in cols:
                    return c
            # try fuzzy
            for col in cols:
                cl = col.lower()
                if any(k in cl for k in candidates):
                    return col
            return None

        prof_candidates = ["professional_development", "professional", "development"]
        pers_candidates = ["personal_growth", "personal", "growth"]

        prof_col = resolve_col(filtered_df.columns, prof_candidates)
        pers_col = resolve_col(filtered_df.columns, pers_candidates)

        rename_map = {}
        if prof_col:
            rename_map[prof_col] = "Professional Development"
        if pers_col:
            rename_map[pers_col] = "Personal Growth"
        if rename_map:
            df_display = df_display.rename(columns=rename_map)

        df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.date
        st.dataframe(df_display.sort_values("Date", ascending=False), width="stretch")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No growth logs yet.")