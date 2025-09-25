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
ws = client.open("nutrition_and_hydration").sheet1

# ---------------- Load Data ----------------
if "nutrition_df" not in st.session_state:
    st.session_state.nutrition_df = pd.DataFrame(ws.get_all_records())

st.title("🍎 Nutrition & Hydration")

today = date.today()

# ---------------- Entry Form ----------------
entry_date = st.date_input("Date", today)

# Find existing record
df_records = st.session_state.nutrition_df.to_dict(orient="records")
existing_row_idx, existing_row = None, None
for i, row in enumerate(df_records):
    if str(row.get("date")) == str(entry_date):
        existing_row_idx = i + 2  # account for header row
        existing_row = row
        break

# Helpers to resolve columns robustly
def resolve_col(record_keys, candidates):
    for c in candidates:
        if c in record_keys:
            return c
    # fuzzy contains
    for k in record_keys:
        kl = k.lower()
        if any(c in kl for c in candidates):
            return k
    return None

def prefill_value(record, candidates, default_val):
    if not record:
        return default_val
    col = resolve_col(record.keys(), candidates)
    return record.get(col, default_val) if col else default_val

# Prefills
prefill_breakfast = str(prefill_value(existing_row, ["breakfast"], ""))
prefill_lunch = str(prefill_value(existing_row, ["lunch"], ""))
prefill_dinner = str(prefill_value(existing_row, ["dinner"], ""))
prefill_snacks = str(prefill_value(existing_row, ["snacks", "snack"], ""))
prefill_supplements = str(prefill_value(existing_row, ["supplements", "supplement"], ""))
prefill_water = prefill_value(existing_row, ["water_ml", "water"], 0)
try:
    prefill_water = int(prefill_water) if str(prefill_water).strip() != "" else 0
except:
    prefill_water = 0

col1, col2 = st.columns(2)
with col1:
    breakfast = st.text_area("Breakfast", value=prefill_breakfast, height=90)
    dinner = st.text_area("Dinner", value=prefill_dinner, height=90)
with col2:
    lunch = st.text_area("Lunch", value=prefill_lunch, height=90)
    snacks = st.text_area("Snacks", value=prefill_snacks, height=90)

col3, col4 = st.columns(2)
with col3:
    supplements = st.text_area("Supplements", value=prefill_supplements, height=90)
with col4:
    water_ml = st.number_input("Water (ml)", min_value=0, step=100, value=int(prefill_water))

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
            ws.update(values=[[breakfast, lunch, dinner, snacks, supplements, int(water_ml)]], range_name=f"B{existing_row_idx}:G{existing_row_idx}")
            st.success(f"Updated nutrition log for {entry_date}.")
        else:
            ws.append_row([str(entry_date), breakfast, lunch, dinner, snacks, supplements, int(water_ml)])
            st.success(f"Added new nutrition log for {entry_date}.")
        st.session_state.nutrition_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

if delete_clicked and existing_row_idx:
    try:
        ws.delete_rows(existing_row_idx)
        st.success(f"Deleted nutrition log for {entry_date}.")
        st.session_state.nutrition_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")

# ---------------- Analytics ----------------
if not st.session_state.nutrition_df.empty:
    df = st.session_state.nutrition_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Date filter (NaT-safe)
    valid_dates = df["date"].dropna()
    if valid_dates.empty:
        st.warning("No valid dates found in the data.")
        st.stop()

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    today_val = date.today()
    try:
        _ = min_date.year  # sanity
    except Exception:
        min_date = today_val
        max_date = today_val

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
        # Interactive table
        df_display = filtered_df.rename(columns={
            "date": "Date",
            "breakfast": "Breakfast",
            "lunch": "Lunch",
            "dinner": "Dinner",
            "snacks": "Snacks",
            "supplements": "Supplements",
            "water_ml": "Water (ml)"
        })

        # Normalize display if original columns are differently named
        for alt, std in [
            ("water", "Water (ml)"),
            ("supplement", "Supplements")
        ]:
            if alt in df_display.columns and std not in df_display.columns:
                df_display = df_display.rename(columns={alt: std})

        df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.date
        st.dataframe(df_display.sort_values("Date", ascending=False), width="stretch")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No nutrition logs yet.")