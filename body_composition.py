import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
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
ws = client.open("body_composition").sheet1  # <-- change sheet name if needed

# ---------------- Load Data ----------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(ws.get_all_records())

st.title("💪 Body Composition")

today = date.today()

# ---------------- Entry Form ----------------
entry_date = st.date_input("Date", today)

# Find existing record
df_records = st.session_state.df.to_dict(orient="records")
existing_row_idx, existing_row = None, None
for i, row in enumerate(df_records):
    if str(row.get("date")) == str(entry_date):
        existing_row_idx = i + 2  # account for header row
        existing_row = row
        break

# Prefill values
prefill_weight = existing_row["weight_lb"] if existing_row else 0.0
prefill_bodyfat = existing_row["body_fat_percent"] if existing_row else 0.0
prefill_muscle = existing_row["skeletal_muscle_percent"] if existing_row else 0.0

with st.form("body_composition_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        weight_lb = st.number_input(
            "Weight (lb)",
            min_value=0.0,
            step=0.1,
            format="%.1f",
            value=float(prefill_weight)
        )
    with col2:
        body_fat = st.number_input(
            "Body Fat (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.1f",
            value=float(prefill_bodyfat)
        )
    with col3:
        muscle = st.number_input(
            "Skeletal Muscle (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.1f",
            value=float(prefill_muscle)
        )

    col_save, col_delete = st.columns([1, 1])
    with col_save:
        save_clicked = st.form_submit_button("💾 Save")
    with col_delete:
        delete_clicked = st.form_submit_button("🗑️ Delete", disabled=(existing_row_idx is None))

# ---------------- Handle Save/Delete ----------------
if save_clicked:
    if existing_row_idx:
        ws.update(values=[[weight_lb, body_fat, muscle]], range_name=f"B{existing_row_idx}:D{existing_row_idx}")
        st.success(f"💾 Updated body composition log for {entry_date}")
    else:
        ws.append_row([str(entry_date), weight_lb, body_fat, muscle])
        st.success(f"✅ Added new body composition log for {entry_date}")
    st.session_state.df = pd.DataFrame(ws.get_all_records())

if delete_clicked and existing_row_idx:
    ws.delete_rows(existing_row_idx)
    st.success(f"🗑️ Deleted body composition log for {entry_date}")
    st.session_state.df = pd.DataFrame(ws.get_all_records())

# ---------------- Analytics ----------------
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["weight_lb"] = pd.to_numeric(df["weight_lb"], errors="coerce")
    df["body_fat_percent"] = pd.to_numeric(df["body_fat_percent"], errors="coerce")
    df["skeletal_muscle_percent"] = pd.to_numeric(df["skeletal_muscle_percent"], errors="coerce")

    st.subheader("📊 Trends")

    # Weight trend
    fig_wt = px.line(
        df.sort_values("date"),
        x="date",
        y="weight_lb",
        markers=True,
        title="Weight Over Time",
        color_discrete_sequence=["#028283"]
    )
    fig_wt.update_layout(template="plotly_white")
    st.plotly_chart(fig_wt, use_container_width=True)

    # Body fat & muscle trend
    fig_bf = px.line(
        df.sort_values("date"),
        x="date",
        y=["body_fat_percent", "skeletal_muscle_percent"],
        markers=True,
        title="Body Fat % and Muscle % Over Time",
        color_discrete_sequence=["#e7541e", "#028283"]
    )
    fig_bf.update_layout(template="plotly_white")
    st.plotly_chart(fig_bf, use_container_width=True)

    # ---------------- Interactive Table ----------------
    df_display = df.rename(columns={
        "date": "Date",
        "weight_lb": "Weight (lb)",
        "body_fat_percent": "Body Fat (%)",
        "skeletal_muscle_percent": "Muscle (%)"
    })
    df_display["Date"] = df_display["Date"].dt.date
    st.dataframe(df_display.sort_values("Date", ascending=False), width="stretch")
else:
    st.info("No body composition logs yet.")