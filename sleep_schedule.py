import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime, timedelta
import plotly.express as px

# ---------------- Helper Functions ----------------
def find_sleep_columns(df):
    """Find sleep start and end columns in the dataframe."""
    sleep_start_col = None
    sleep_end_col = None
    
    # Check for expected column names first
    if "sleep_start" in df.columns:
        sleep_start_col = "sleep_start"
    elif "sleep_end" in df.columns:
        sleep_end_col = "sleep_end"
    
    # If not found, search for alternative names
    if not sleep_start_col:
        possible_start_cols = [col for col in df.columns if 'start' in col.lower() or 'sleep' in col.lower()]
        sleep_start_col = possible_start_cols[0] if possible_start_cols else None
    
    if not sleep_end_col:
        possible_end_cols = [col for col in df.columns if 'end' in col.lower() or 'wake' in col.lower()]
        sleep_end_col = possible_end_cols[0] if possible_end_cols else None
    
    # Fallback to positional columns
    if not sleep_start_col and len(df.columns) > 1:
        sleep_start_col = df.columns[1]
    if not sleep_end_col and len(df.columns) > 2:
        sleep_end_col = df.columns[2]
    
    return sleep_start_col, sleep_end_col


def parse_time_safe(time_series):
    """Safely parse time values from a series with multiple format support."""
    parsed_times = []
    for time_val in time_series:
        if pd.isna(time_val) or str(time_val).strip() == '':
            parsed_times.append(None)
            continue
        
        time_str = str(time_val).strip()
        try:
            # Try HH:MM format first (most common)
            if ':' in time_str and len(time_str.split(':')) == 2:
                hour, minute = time_str.split(':')
                if hour.isdigit() and minute.isdigit():
                    parsed_time = time(int(hour), int(minute))
                    parsed_times.append(parsed_time)
                    continue
            
            # Try other common formats
            for fmt in ['%H:%M', '%I:%M %p', '%I:%M%p', '%H.%M']:
                try:
                    parsed_time = datetime.strptime(time_str, fmt).time()
                    parsed_times.append(parsed_time)
                    break
                except ValueError:
                    continue
            else:
                # If no format works, skip this value
                parsed_times.append(None)
        except:
            parsed_times.append(None)
    
    return parsed_times


def clean_sleep_data(df, sleep_start_col, sleep_end_col):
    """Clean and parse sleep data from the dataframe."""
    try:
        # Clean the data first - remove any empty or invalid values
        df_clean = df.dropna(subset=[sleep_start_col, sleep_end_col])
        df_clean = df_clean[df_clean[sleep_start_col].astype(str).str.strip() != '']
        df_clean = df_clean[df_clean[sleep_end_col].astype(str).str.strip() != '']
        
        if df_clean.empty:
            return None
        
        # Parse time values
        df_clean["sleep_start"] = parse_time_safe(df_clean[sleep_start_col])
        df_clean["sleep_end"] = parse_time_safe(df_clean[sleep_end_col])
        
        # Remove rows where time parsing failed
        df_clean = df_clean.dropna(subset=["sleep_start", "sleep_end"])
        
        return df_clean if not df_clean.empty else None
        
    except Exception as e:
        st.error(f"Error parsing time data: {str(e)}")
        return None


def get_prefill_times(existing_row):
    """Get prefill times from existing row data."""
    if not existing_row:
        return default_start, default_end
    
    # Find sleep columns in existing row
    start_col, end_col = find_sleep_columns(pd.DataFrame([existing_row]))
    
    if start_col and end_col and existing_row.get(start_col) and existing_row.get(end_col):
        try:
            start_str = str(existing_row[start_col]).strip()
            end_str = str(existing_row[end_col]).strip()
            
            if start_str and end_str:
                # Try multiple time formats
                for fmt in ['%H:%M', '%I:%M %p', '%I:%M%p', '%H.%M']:
                    try:
                        prefill_start = datetime.strptime(start_str, fmt).time()
                        prefill_end = datetime.strptime(end_str, fmt).time()
                        return prefill_start, prefill_end
                    except ValueError:
                        continue
        except:
            pass
    
    return default_start, default_end


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
ws = client.open("sleep_schedule").sheet1

# ---------------- Load Data ----------------
if "sleep_df" not in st.session_state:
    st.session_state.sleep_df = pd.DataFrame(ws.get_all_records())

st.title("🧸 Sleep Schedule")

today = date.today()
default_start = time(22, 0)
default_end = time(6, 0)

# ---------------- Sleep Entry ----------------
entry_date = st.date_input("Date", today)

# Find existing record
df_records = st.session_state.sleep_df.to_dict(orient="records")
existing_row_idx = None
existing_row = None
for i, row in enumerate(df_records):
    if str(row.get("date")) == str(entry_date):
        existing_row_idx = i + 2  # account for header row
        existing_row = row
        break

# Prefill values if record exists
prefill_start, prefill_end = get_prefill_times(existing_row)

col1, col2 = st.columns(2)
sleep_start = col1.time_input("Sleep Start", prefill_start)
sleep_end = col2.time_input("Sleep End", prefill_end)

# ---------------- Action Buttons ----------------
col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

# ---------------- Handle Save/Delete ----------------
if save_clicked:
    start_str, end_str = sleep_start.strftime("%H:%M"), sleep_end.strftime("%H:%M")
    if existing_row_idx:
        ws.update(values=[[start_str, end_str]], range_name=f"B{existing_row_idx}:C{existing_row_idx}")
        st.success(f"Updated sleep log for {entry_date}.")
    else:
        ws.append_row([str(entry_date), start_str, end_str])
        st.success(f"Added new sleep log for {entry_date}.")
    st.session_state.sleep_df = pd.DataFrame(ws.get_all_records())

if delete_clicked and existing_row_idx:
    ws.delete_rows(existing_row_idx)
    st.success(f"Deleted sleep log for {entry_date}.")
    st.session_state.sleep_df = pd.DataFrame(ws.get_all_records())

# ---------------- Analytics ----------------
if not st.session_state.sleep_df.empty:
    df = st.session_state.sleep_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    # Find sleep columns
    sleep_start_col, sleep_end_col = find_sleep_columns(df)
    
    if not sleep_start_col or not sleep_end_col:
        st.error("Could not find sleep start and end time columns in the data.")
        st.stop()
    
    # Clean and parse the data
    df_clean = clean_sleep_data(df, sleep_start_col, sleep_end_col)
    
    if df_clean is None:
        st.warning("No valid sleep data found in the selected columns.")
        st.stop()
    
    df = df_clean

    # Compute sleep duration in hours
    def calc_duration(row):
        start_dt = datetime.combine(row["date"], row["sleep_start"])
        end_dt = datetime.combine(row["date"], row["sleep_end"])
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        return round((end_dt - start_dt).total_seconds() / 3600, 2)

    df["Sleep Duration (hrs)"] = df.apply(calc_duration, axis=1)

    # Compute average times
    def average_time(times):
        seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in times]
        avg_seconds = sum(seconds) / len(seconds)
        h = int(avg_seconds // 3600) % 24
        m = int((avg_seconds % 3600) // 60)
        return time(h, m)

    # ---------------- Date Filter + Metrics ----------------
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    # Handle potential NaT values in date columns
    valid_dates = df["date"].dropna()
    if valid_dates.empty:
        st.warning("No valid dates found in the data.")
        st.stop()
    
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    
    # Use today's date as fallback if min/max dates are invalid
    today = date.today()
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = today
        max_date = today
    
    start_filter = col1.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_filter = col2.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

    filtered_df = pd.DataFrame()
    if start_filter > end_filter:
        st.warning("⚠️ Invalid date range: Start Date cannot be after End Date.")
    else:
        filtered_df = df[(df["date"].dt.date >= start_filter) & (df["date"].dt.date <= end_filter)].copy()

    if not filtered_df.empty:
        avg_start = average_time(filtered_df["sleep_start"])
        avg_end = average_time(filtered_df["sleep_end"])
        avg_duration = filtered_df["Sleep Duration (hrs)"].mean()

        col3.metric("Avg. Sleep Start", avg_start.strftime("%H:%M"))
        col4.metric("Avg. Sleep End", avg_end.strftime("%H:%M"))
        col5.metric("Avg. Sleep Duration (hrs)", f"{avg_duration:.2f}")

        # ---------------- Line Chart ----------------
        duration_chart = filtered_df[["date", "Sleep Duration (hrs)"]].sort_values("date")
        fig = px.line(
            duration_chart,
            x="date",
            y="Sleep Duration (hrs)",
            markers=True,
            color_discrete_sequence=["#028283"]
        )
        fig.add_hline(
            y=7,
            line_dash="dash",
            line_color="#e7541e",
            annotation_text="Target: 7.0 hrs",
            annotation_position="top left"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Sleep Duration (hrs)",
            xaxis=dict(
                tickformat="%d %b",
                tickangle=0,
                showgrid=False,
                showline=False
            ),
            yaxis=dict(
                range=[duration_chart["Sleep Duration (hrs)"].min() - 0.5,
                       duration_chart["Sleep Duration (hrs)"].max() + 0.5],
                showgrid=False
            ),
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---------------- Interactive Table ----------------
        df_display = filtered_df.rename(columns={
            "date": "Date",
            "sleep_start": "Sleep Start",
            "sleep_end": "Sleep End"
        })
        df_display["Date"] = df_display["Date"].dt.date
        df_display["Sleep Start"] = df_display["Sleep Start"].apply(lambda t: t.strftime("%H:%M"))
        df_display["Sleep End"] = df_display["Sleep End"].apply(lambda t: t.strftime("%H:%M"))

        st.dataframe(df_display.sort_values("Date", ascending=False), width='stretch')
else:
    st.info("No sleep logs yet.")