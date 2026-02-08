import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("mood_and_gratitude").sheet1

if "growth_df" not in st.session_state:
    st.session_state.growth_df = pd.DataFrame(ws.get_all_records())

st.title("🌱 Mood & Gratitude")

today = date.today()

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
    mood_key = None
    gratitude_key = None
    for col in record.keys():
        cl = col.lower()
        if mood_key is None and "mood" in cl:
            mood_key = col
        if gratitude_key is None and "gratitude" in cl:
            gratitude_key = col
    # Fallback order-based if not found
    keys = list(record.keys())
    if mood_key is None and len(keys) > 1:
        mood_key = keys[1]
    if gratitude_key is None and len(keys) > 2:
        gratitude_key = keys[2]
    return mood_key, gratitude_key

if existing_row:
    mood_col, gratitude_col = find_cols(existing_row)
    prefill_mood = str(existing_row.get(mood_col, "")) if mood_col else ""
    prefill_gratitude = str(existing_row.get(gratitude_col, "")) if gratitude_col else ""
else:
    prefill_mood = ""
    prefill_gratitude = ""

col1, col2 = st.columns(2)
with col1:
    mood_options = [
        "😀 cheerful and upbeat",
        "😄 good and content", 
        "😊 calm and satisfied",
        "😍 joyful or enthusiastic",
        "🥰 grateful or affectionate",
        "🙂 okay, balanced",
        "😐 neither good nor bad",
        "😶 indifferent or unsure",
        "😌 relaxed or at peace",
        "😞 sad or let down",
        "😔 down or reflective",
        "😟 anxious or concerned",
        "😢 upset or emotional",
        "😫 drained or overwhelmed"
    ]
    mood_index = 0
    if prefill_mood and prefill_mood in mood_options:
        mood_index = mood_options.index(prefill_mood)
    mood = st.selectbox(
        "Mood",
        options=mood_options,
        index=mood_index
    )
with col2:
    gratitude = st.text_area(
        "Gratitude",
        value=prefill_gratitude,
        height=100,
        placeholder="What are you grateful for today?"
    )

col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

if save_clicked:
    try:
        if existing_row_idx:
            ws.update(values=[[mood, gratitude]], range_name=f"B{existing_row_idx}:C{existing_row_idx}")
            st.success(f"Updated mood log for {entry_date}.")
        else:
            ws.append_row([str(entry_date), mood, gratitude])
            st.success(f"Added new mood log for {entry_date}.")
        st.session_state.growth_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

if delete_clicked and existing_row_idx:
    try:
        ws.delete_rows(existing_row_idx)
        st.success(f"Deleted mood log for {entry_date}.")
        st.session_state.growth_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")

if not st.session_state.growth_df.empty:
    df = st.session_state.growth_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    valid_dates = df["date"].dropna()
    if valid_dates.empty:
        st.warning("No valid dates found in the data.")
        st.stop()

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    today_val = date.today()
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = today_val
        max_date = today_val

    st.write("")
    st.write("")
    header_col, filter_col1, filter_col2 = st.columns([2, 1, 1])
    
    with header_col:
        st.subheader("Mood & Gratitude Analysis")
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
        # Interactive Table
        df_display = filtered_df.rename(columns={
            "date": "Date",
        })

        def resolve_col(cols, candidates):
            for c in candidates:
                if c in cols:
                    return c
            for col in cols:
                cl = col.lower()
                if any(k in cl for k in candidates):
                    return col
            return None

        mood_candidates = ["mood"]
        gratitude_candidates = ["gratitude"]

        mood_col = resolve_col(filtered_df.columns, mood_candidates)
        gratitude_col = resolve_col(filtered_df.columns, gratitude_candidates)

        rename_map = {}
        if mood_col:
            rename_map[mood_col] = "Mood"
        if gratitude_col:
            rename_map[gratitude_col] = "Gratitude"
        if rename_map:
            df_display = df_display.rename(columns=rename_map)

        df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.date
        with st.expander("Log Entries", expanded=False):
            st.dataframe(df_display.sort_values("Date", ascending=False), width="stretch")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No mood logs yet.")