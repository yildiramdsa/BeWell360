import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

# ---------------- Configuration ----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("the_yukon_63k").sheet1

GOAL_KM = 63
WINTER_MONTHS = {12, 1, 2}  # December, January, February

st.title("❄️ The Yukon 63K")

st.info(
    "**Did you know?**\n\nThe coldest temperature ever recorded in Canada was 63.0 °C below zero in Snag, Yukon on February 3, 1947.\n\n"
    "To honor that record, log 63 km total during the winter months (December, January, February) using distance based activities such as running, walking, cycling, hiking, snowshoeing, cross country skiing, or any activity that tracks distance."
)

# Initialize session state
if "challenge_data" not in st.session_state:
    st.session_state.challenge_data = pd.DataFrame()

# Load user data
try:
    st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
except Exception:
    st.session_state.challenge_data = pd.DataFrame()

# Calculate total distance logged (only winter months count)
total_logged = 0.0
if not st.session_state.challenge_data.empty:
    df = st.session_state.challenge_data
    date_col = "date" if "date" in df.columns else df.columns[0]
    dist_col = "distance_km" if "distance_km" in df.columns else (df.columns[1] if len(df.columns) > 1 else None)

    if dist_col:
        df["_parsed_date"] = pd.to_datetime(df[date_col], errors="coerce")
        winter_rows = df[df["_parsed_date"].apply(lambda x: x.month in WINTER_MONTHS if pd.notna(x) else False)]
        total_logged = winter_rows[dist_col].fillna(0).astype(float).sum()

st.markdown("### Your Progress")

col1, col2, col3 = st.columns(3)
with col1:
    st.write(f"**Distance (winter months):** {total_logged:,.1f} km")
with col2:
    remaining = max(0, GOAL_KM - total_logged)
    st.write(f"**Remaining:** {remaining:,.1f} km")
with col3:
    if total_logged >= GOAL_KM:
        st.write("**Status:** 🏆 Complete!")
    else:
        st.write(f"**Goal:** {GOAL_KM} km")

# Progress bar
progress_pct = min((total_logged / GOAL_KM) * 100, 100)
st.progress(progress_pct / 100)
st.caption(f"Progress: {progress_pct:.1f}%")

if total_logged >= GOAL_KM:
    st.success("**Congratulations!** You've completed The Yukon 63K!")

st.markdown("### Log Your Kilometers")


def get_existing_distance(selected_date):
    date_str = str(selected_date)
    existing_data = st.session_state.challenge_data
    if not existing_data.empty and "date" in existing_data.columns:
        date_exists = existing_data["date"].astype(str).str.contains(date_str).any()
        if date_exists:
            row = existing_data[existing_data["date"].astype(str) == date_str].iloc[0]
            dist_col = "distance_km" if "distance_km" in existing_data.columns else existing_data.columns[1]
            return float(row[dist_col]) if pd.notna(row[dist_col]) else 0.0
    elif not existing_data.empty and len(existing_data.columns) >= 2:
        date_col = existing_data.columns[0]
        date_exists = existing_data[date_col].astype(str).str.contains(date_str).any()
        if date_exists:
            row = existing_data[existing_data[date_col].astype(str) == date_str].iloc[0]
            return float(row.iloc[1]) if pd.notna(row.iloc[1]) else 0.0
    return 0.0


activity_date = st.date_input("Date", value=date.today())
existing_distance = get_existing_distance(activity_date)

if existing_distance > 0:
    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=existing_distance,
                               help=f"Currently logged: {existing_distance} km for {activity_date}")
else:
    distance = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=0.0,
                               help=f"No activity logged for {activity_date}")

in_winter = activity_date.month in WINTER_MONTHS
if not in_winter:
    st.caption("ℹ️ Only December, January, and February count toward the 63 km goal. You can still log other months for your records.")

if st.button("Log Activity"):
    if distance >= 0:
        try:
            date_str = str(activity_date)
            existing_data = st.session_state.challenge_data

            if not existing_data.empty and ("date" in existing_data.columns or len(existing_data.columns) >= 1):
                date_col = "date" if "date" in existing_data.columns else existing_data.columns[0]
                date_exists = existing_data[date_col].astype(str).str.contains(date_str).any()

                if date_exists:
                    row_index = existing_data[existing_data[date_col].astype(str) == date_str].index[0]
                    if "distance_km" in existing_data.columns:
                        ws.update(f"B{row_index + 2}", [[distance]])
                    else:
                        ws.update(f"A{row_index + 2}:B{row_index + 2}", [[date_str, distance]])
                    st.success(f"Updated activity for {activity_date}!")
                else:
                    ws.append_row([date_str, distance])
                    st.success("Activity logged successfully!")
            else:
                ws.append_row([date_str, distance])
                st.success("Activity logged successfully!")

            st.session_state.challenge_data = pd.DataFrame(ws.get_all_records())
            st.rerun()
        except Exception as e:
            st.error(f"Error logging activity: {str(e)}")

if not st.session_state.challenge_data.empty:
    with st.expander("Recent Logs", expanded=False):
        df_display = st.session_state.challenge_data.copy()
        if "date" not in df_display.columns and len(df_display.columns) >= 2:
            df_display.columns = ["date", "distance_km"] + list(df_display.columns[2:])
        if "date" in df_display.columns:
            df_display["date"] = pd.to_datetime(df_display["date"], errors="coerce")
            df_display["Counts toward goal"] = df_display["date"].apply(lambda x: "Yes" if x.month in WINTER_MONTHS else "No")
            df_display = df_display.sort_values("date", ascending=False)
            df_display = df_display.drop(columns=["date"])
        st.dataframe(df_display, use_container_width=True)

if total_logged >= GOAL_KM:
    st.balloons()
    st.success("You've conquered The Yukon 63K!")
