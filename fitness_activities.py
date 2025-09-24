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
ws = client.open("fitness_activities").sheet1

# ---------------- Load Data ----------------
if "fitness_df" not in st.session_state:
    st.session_state.fitness_df = pd.DataFrame(ws.get_all_records())

st.title("⚽ Fitness Activities")

today = date.today()

# ---------------- Entry Form ----------------
entry_date = st.date_input("Date", today)

# Find existing record by (date, exercise)
df_records = st.session_state.fitness_df.to_dict(orient="records")
existing_row_idx, existing_row = None, None

def match_row(row, d, ex):
    row_date = str(row.get("date"))
    row_ex = str(row.get("exercise", "")).strip().lower()
    return row_date == str(d) and row_ex == ex.strip().lower()

# Exercise name input first so we can search
exercise = st.text_input("Exercise", value="")

if exercise:
    for i, row in enumerate(df_records):
        if match_row(row, entry_date, exercise):
            existing_row_idx = i + 2  # account for header row
            existing_row = row
            break

def as_int(val, default=0):
    try:
        if val is None or str(val).strip() == "":
            return default
        return int(float(val))
    except:
        return default

def as_float(val, default=0.0):
    try:
        if val is None or str(val).strip() == "":
            return default
        return float(val)
    except:
        return default

# Prefills
prefill_sets = as_int(existing_row.get("sets")) if existing_row else 0
prefill_reps = as_int(existing_row.get("reps")) if existing_row else 0
prefill_weight = as_float(existing_row.get("weight_lb")) if existing_row else 0.0
prefill_duration = as_int(existing_row.get("duration_sec")) if existing_row else 0
prefill_distance = as_float(existing_row.get("distance_km")) if existing_row else 0.0

col1, col2, col3 = st.columns(3)
with col1:
    sets = st.number_input("Sets", min_value=0, step=1, value=int(prefill_sets))
with col2:
    reps = st.number_input("Reps", min_value=0, step=1, value=int(prefill_reps))
with col3:
    weight_lb = st.number_input("Weight (lb)", min_value=0.0, step=1.0, value=float(prefill_weight))

col4, col5 = st.columns(2)
with col4:
    duration_sec = st.number_input("Duration (sec)", min_value=0, step=10, value=int(prefill_duration))
with col5:
    distance_km = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=float(prefill_distance))

# ---------------- Action Buttons ----------------
col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

# ---------------- Handle Save/Delete ----------------
if save_clicked:
    try:
        if not exercise.strip():
            st.error("Exercise name is required.")
        else:
            if existing_row_idx:
                ws.update(
                    values=[[exercise, int(sets), int(reps), float(weight_lb), int(duration_sec), float(distance_km)]],
                    range_name=f"B{existing_row_idx}:G{existing_row_idx}"
                )
                st.success(f"Updated fitness log for {entry_date} - {exercise}.")
            else:
                ws.append_row([
                    str(entry_date),
                    exercise,
                    int(sets),
                    int(reps),
                    float(weight_lb),
                    int(duration_sec),
                    float(distance_km)
                ])
                st.success(f"Added new fitness log for {entry_date} - {exercise}.")
            st.session_state.fitness_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

if delete_clicked and existing_row_idx:
    try:
        ws.delete_rows(existing_row_idx)
        st.success(f"Deleted fitness log for {entry_date} - {exercise}.")
        st.session_state.fitness_df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")

# ---------------- Analytics ----------------
if not st.session_state.fitness_df.empty:
    df = st.session_state.fitness_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["sets"] = pd.to_numeric(df.get("sets", 0), errors="coerce")
    df["reps"] = pd.to_numeric(df.get("reps", 0), errors="coerce")
    df["weight_lb"] = pd.to_numeric(df.get("weight_lb", 0), errors="coerce")
    df["duration_sec"] = pd.to_numeric(df.get("duration_sec", 0), errors="coerce")
    df["distance_km"] = pd.to_numeric(df.get("distance_km", 0.0), errors="coerce")

    # Date filter (NaT-safe)
    valid_dates = df["date"].dropna()
    if valid_dates.empty:
        st.warning("No valid dates found in the data.")
        st.stop()

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    today_val = date.today()
    try:
        _ = min_date.year
    except Exception:
        min_date = today_val
        max_date = today_val

    # Metrics on same row as filters
    filter_col1, filter_col2, metric_col1, metric_col2, metric_col3 = st.columns([1, 1, 1, 1, 1])
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
        # Metrics
        # Training volume (approx): sum(sets * reps * weight) where present
        volume = (filtered_df[["sets", "reps", "weight_lb"]]
                  .prod(axis=1, min_count=1)).sum(skipna=True)
        total_duration_min = filtered_df["duration_sec"].sum(skipna=True) / 60.0
        total_distance_km = filtered_df["distance_km"].sum(skipna=True)

        with metric_col1:
            st.metric("Total Volume", f"{volume:,.0f}")
        with metric_col2:
            st.metric("Total Duration (min)", f"{total_duration_min:.1f}")
        with metric_col3:
            st.metric("Total Distance (km)", f"{total_distance_km:.2f}")

        # ---------------- Weight Progression Chart ----------------
        # Only include entries where weight is present (> 0)
        weighted_df = filtered_df.copy()
        weighted_df["weight_lb"] = pd.to_numeric(weighted_df.get("weight_lb", 0), errors="coerce")
        weighted_df = weighted_df.dropna(subset=["weight_lb"]) 
        weighted_df = weighted_df[weighted_df["weight_lb"] > 0]

        exercises_with_weight = (
            weighted_df["exercise"].dropna().astype(str).sort_values().unique().tolist()
        )
        sel_col1, _ = st.columns([1, 3])
        with sel_col1:
            selected_exercise = st.selectbox(
                "Exercise (weight):",
                options=exercises_with_weight,
                index=0 if exercises_with_weight else None,
                disabled=(len(exercises_with_weight) == 0)
            )
        if exercises_with_weight:
            ex_df = weighted_df[weighted_df["exercise"].astype(str) == selected_exercise].copy()
            ex_df = ex_df.sort_values("date")
            if not ex_df.empty:
                import plotly.express as px
                fig_w = px.line(
                    ex_df,
                    x="date",
                    y="weight_lb",
                    markers=True,
                    color_discrete_sequence=["#028283"],
                    title=f"Weight over Time • {selected_exercise}"
                )
                fig_w.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Weight (lb)",
                    xaxis=dict(
                        tickformat="%d %b",
                        tickangle=0,
                        showgrid=False,
                        showline=False,
                        zeroline=False
                    ),
                    yaxis=dict(
                        showgrid=False,
                        showline=False,
                        zeroline=False
                    ),
                    template="plotly_white"
                )
                st.plotly_chart(fig_w, use_container_width=True)

        # Interactive table
        df_display = filtered_df.rename(columns={
            "date": "Date",
            "exercise": "Exercise",
            "sets": "Sets",
            "reps": "Reps",
            "weight_lb": "Weight (lb)",
            "duration_sec": "Duration (sec)",
            "distance_km": "Distance (km)"
        })
        df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.date
        st.dataframe(df_display.sort_values(["Date", "Exercise"], ascending=[False, True]), width="stretch")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No fitness logs yet.")