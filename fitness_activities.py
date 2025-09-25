import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# Google Sheets Setup
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

# Load Data
if "fitness_df" not in st.session_state:
    st.session_state.fitness_df = pd.DataFrame(ws.get_all_records())

st.title("⚽ Fitness Activities")

today = date.today()

# Entry Form
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

# Action Buttons
col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

# Handle Save/Delete
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

# Analytics
if not st.session_state.fitness_df.empty:
    df = st.session_state.fitness_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["sets"] = pd.to_numeric(df.get("sets", 0), errors="coerce")
    df["reps"] = pd.to_numeric(df.get("reps", 0), errors="coerce")
    df["weight_lb"] = pd.to_numeric(df.get("weight_lb", 0), errors="coerce")
    df["duration_sec"] = pd.to_numeric(df.get("duration_sec", 0), errors="coerce")
    df["distance_km"] = pd.to_numeric(df.get("distance_km", 0.0), errors="coerce")

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

    # Results Section
    st.write("")
    st.write("")
    header_col, filter_col1, filter_col2 = st.columns([2, 1, 1])
    
    with header_col:
        st.subheader("Fitness Activities Analysis")
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
        # Weight Progression Chart
        weighted_df = filtered_df.copy()
        weighted_df["weight_lb"] = pd.to_numeric(weighted_df.get("weight_lb", 0), errors="coerce")
        weighted_df = weighted_df.dropna(subset=["weight_lb"]) 
        weighted_df = weighted_df[weighted_df["weight_lb"] > 0]

        exercises_with_weight = (
            weighted_df["exercise"].dropna().astype(str).sort_values().unique().tolist()
        )
        
        sel_col1, weight_col1, weight_col2, weight_col3 = st.columns([2, 1, 1, 1])
        with sel_col1:
            selected_exercise = st.selectbox(
                "Exercise (weight):",
                options=exercises_with_weight if exercises_with_weight else ["No weight data"],
                index=0 if exercises_with_weight else None,
                disabled=(len(exercises_with_weight) == 0)
            )
        
        with weight_col1:
            if exercises_with_weight and selected_exercise != "No weight data":
                selected_exercise_data = weighted_df[weighted_df["exercise"].astype(str) == selected_exercise]
                if not selected_exercise_data.empty:
                    min_weight_selected = selected_exercise_data["weight_lb"].min()
                    st.metric("Min Weight (lb)", f"{min_weight_selected:.1f}")
                else:
                    st.metric("Min Weight (lb)", "N/A")
            else:
                st.metric("Min Weight (lb)", "N/A")
        
        with weight_col2:
            if exercises_with_weight and selected_exercise != "No weight data":
                selected_exercise_data = weighted_df[weighted_df["exercise"].astype(str) == selected_exercise]
                if not selected_exercise_data.empty:
                    avg_weight_selected = selected_exercise_data["weight_lb"].mean()
                    st.metric("Avg Weight (lb)", f"{avg_weight_selected:.1f}")
                else:
                    st.metric("Avg Weight (lb)", "N/A")
            else:
                st.metric("Avg Weight (lb)", "N/A")
        
        with weight_col3:
            if exercises_with_weight and selected_exercise != "No weight data":
                selected_exercise_data = weighted_df[weighted_df["exercise"].astype(str) == selected_exercise]
                if not selected_exercise_data.empty:
                    max_weight_selected = selected_exercise_data["weight_lb"].max()
                    st.metric("Max Weight (lb)", f"{max_weight_selected:.1f}")
                else:
                    st.metric("Max Weight (lb)", "N/A")
            else:
                st.metric("Max Weight (lb)", "N/A")
        
        if exercises_with_weight and selected_exercise != "No weight data":
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
                    title=f"Weight Over Time • {selected_exercise}"
                )
                avg_weight = ex_df["weight_lb"].mean()
                fig_w.add_hline(
                    y=avg_weight,
                    line_dash="dash",
                    line_color="#e7541e",
                    annotation_text=f"Avg: {avg_weight:.1f} lb",
                    annotation_position="top left"
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
        else:
            st.info("No exercises with weight data in the selected range.")

        # Distance Progression Chart
        distance_df = filtered_df.copy()
        distance_df["distance_km"] = pd.to_numeric(distance_df.get("distance_km", 0), errors="coerce")
        distance_df = distance_df.dropna(subset=["distance_km"]) 
        distance_df = distance_df[distance_df["distance_km"] > 0]

        exercises_with_distance = (
            distance_df["exercise"].dropna().astype(str).sort_values().unique().tolist()
        )
        
        sel_col2, dist_col1, dist_col2, dist_col3, dist_col4 = st.columns([1, 1, 1, 1, 1])
        with sel_col2:
            selected_exercise_dist = st.selectbox(
                "Exercise (distance):",
                options=exercises_with_distance if exercises_with_distance else ["No distance data"],
                index=0 if exercises_with_distance else None,
                disabled=(len(exercises_with_distance) == 0)
            )
        
        with dist_col1:
            if exercises_with_distance and selected_exercise_dist != "No distance data":
                selected_exercise_dist_data = distance_df[distance_df["exercise"].astype(str) == selected_exercise_dist]
                if not selected_exercise_dist_data.empty:
                    min_distance_selected = selected_exercise_dist_data["distance_km"].min()
                    st.metric("Min Distance (km)", f"{min_distance_selected:.2f}")
                else:
                    st.metric("Min Distance (km)", "N/A")
            else:
                st.metric("Min Distance (km)", "N/A")
        
        with dist_col2:
            if exercises_with_distance and selected_exercise_dist != "No distance data":
                selected_exercise_dist_data = distance_df[distance_df["exercise"].astype(str) == selected_exercise_dist]
                if not selected_exercise_dist_data.empty:
                    avg_distance_selected = selected_exercise_dist_data["distance_km"].mean()
                    st.metric("Avg Distance (km)", f"{avg_distance_selected:.2f}")
                else:
                    st.metric("Avg Distance (km)", "N/A")
            else:
                st.metric("Avg Distance (km)", "N/A")
        
        with dist_col3:
            if exercises_with_distance and selected_exercise_dist != "No distance data":
                selected_exercise_dist_data = distance_df[distance_df["exercise"].astype(str) == selected_exercise_dist]
                if not selected_exercise_dist_data.empty:
                    max_distance_selected = selected_exercise_dist_data["distance_km"].max()
                    st.metric("Max Distance (km)", f"{max_distance_selected:.2f}")
                else:
                    st.metric("Max Distance (km)", "N/A")
            else:
                st.metric("Max Distance (km)", "N/A")
        
        with dist_col4:
            if exercises_with_distance and selected_exercise_dist != "No distance data":
                selected_exercise_dist_data = distance_df[distance_df["exercise"].astype(str) == selected_exercise_dist]
                if not selected_exercise_dist_data.empty:
                    total_distance_selected = selected_exercise_dist_data["distance_km"].sum()
                    st.metric("Total Distance (km)", f"{total_distance_selected:.2f}")
                else:
                    st.metric("Total Distance (km)", "N/A")
            else:
                st.metric("Total Distance (km)", "N/A")
        
        if exercises_with_distance and selected_exercise_dist != "No distance data":
            ex_df_dist = distance_df[distance_df["exercise"].astype(str) == selected_exercise_dist].copy()
            ex_df_dist = ex_df_dist.sort_values("date")
            if not ex_df_dist.empty:
                import plotly.express as px
                fig_d = px.line(
                    ex_df_dist,
                    x="date",
                    y="distance_km",
                    markers=True,
                    color_discrete_sequence=["#e7541e"],
                    title=f"Distance Over Time • {selected_exercise_dist}"
                )
                avg_distance = ex_df_dist["distance_km"].mean()
                fig_d.add_hline(
                    y=avg_distance,
                    line_dash="dash",
                    line_color="#028283",
                    annotation_text=f"Avg: {avg_distance:.2f} km",
                    annotation_position="top left"
                )
                fig_d.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Distance (km)",
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
                st.plotly_chart(fig_d, use_container_width=True)
        else:
            st.info("No exercises with distance data in the selected range.")

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
        with st.expander("Log Entries", expanded=False):
            st.dataframe(df_display.sort_values(["Date", "Exercise"], ascending=[False, True]), width="stretch")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No fitness logs yet.")