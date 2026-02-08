import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime, timedelta
import plotly.express as px


def find_sleep_columns(df):
    sleep_start_col = None
    sleep_end_col = None
    
    if "sleep_start_datetime" in df.columns:
        sleep_start_col = "sleep_start_datetime"
    elif "sleep_start" in df.columns:
        sleep_start_col = "sleep_start"
    if "sleep_end_datetime" in df.columns:
        sleep_end_col = "sleep_end_datetime"
    elif "sleep_end" in df.columns:
        sleep_end_col = "sleep_end"
    
    if not sleep_start_col:
        possible_start_cols = [col for col in df.columns if 'start' in col.lower() or 'sleep' in col.lower()]
        sleep_start_col = possible_start_cols[0] if possible_start_cols else None
    
    if not sleep_end_col:
        possible_end_cols = [col for col in df.columns if 'end' in col.lower() or 'wake' in col.lower()]
        sleep_end_col = possible_end_cols[0] if possible_end_cols else None
    
    if not sleep_start_col and len(df.columns) >= 1:
        sleep_start_col = df.columns[0]
    if not sleep_end_col and len(df.columns) >= 2:
        sleep_end_col = df.columns[1]
    
    return sleep_start_col, sleep_end_col


def parse_datetime_safe(series, default_date=None, date_series=None):
    """Parse series of datetime or time strings to datetime objects. If date_series is provided, use it for time-only parsing (per-row date)."""
    if default_date is None:
        default_date = date.today()
    parsed = []
    for i, val in enumerate(series):
        if pd.isna(val) or str(val).strip() == '':
            parsed.append(pd.NaT)
            continue
        row_date = date_series.iloc[i] if date_series is not None and i < len(date_series) else default_date
        if hasattr(row_date, 'date'):
            row_date = row_date.date() if callable(getattr(row_date, 'date', None)) else row_date
        s = str(val).strip()
        dt = None
        for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S',
                    '%d/%m/%Y %H:%M', '%m/%d/%Y %H:%M', '%H:%M', '%H:%M:%S', '%Y-%m-%d']:
            try:
                dt = datetime.strptime(s[:19] if len(s) > 19 else s, fmt)
                if fmt in ('%H:%M', '%H:%M:%S'):
                    dt = datetime.combine(row_date, dt.time())
                elif fmt == '%Y-%m-%d':
                    dt = datetime.combine(dt.date(), time(0, 0))
                parsed.append(dt)
                break
            except (ValueError, TypeError):
                continue
        if dt is None:
            parsed.append(pd.NaT)
    return parsed


def clean_sleep_data(df, sleep_start_col, sleep_end_col):
    """Clean and parse sleep data from the dataframe."""
    try:
        # Clean the data first - remove any empty or invalid values
        df_clean = df.dropna(subset=[sleep_start_col, sleep_end_col])
        df_clean = df_clean[df_clean[sleep_start_col].astype(str).str.strip() != '']
        df_clean = df_clean[df_clean[sleep_end_col].astype(str).str.strip() != '']
        
        if df_clean.empty:
            return None
        
        # If sheet has a date column (old format), use it when parsing time-only
        date_series = None
        if "date" in df_clean.columns:
            df_clean["date"] = pd.to_datetime(df_clean["date"])
            date_series = df_clean["date"]
        
        # Parse datetime values (support both datetime and time-only for backward compat)
        df_clean["sleep_start_datetime"] = parse_datetime_safe(df_clean[sleep_start_col], date_series=date_series)
        df_clean["sleep_end_datetime"] = parse_datetime_safe(df_clean[sleep_end_col], date_series=date_series)
        
        # Remove rows where parsing failed
        df_clean = df_clean.dropna(subset=["sleep_start_datetime", "sleep_end_datetime"])
        # Derive date from sleep_start for filtering/charts
        df_clean["date"] = pd.to_datetime(df_clean["sleep_start_datetime"]).dt.normalize()
        
        return df_clean if not df_clean.empty else None
        
    except Exception as e:
        st.error(f"Error parsing datetime data: {str(e)}")
        return None


def get_prefill_datetimes(existing_row, default_start, default_end):
    """Get prefill datetimes from existing row data."""
    if not existing_row:
        return default_start, default_end
    
    start_col, end_col = find_sleep_columns(pd.DataFrame([existing_row]))
    if not start_col or not end_col or not existing_row.get(start_col) or not existing_row.get(end_col):
        return default_start, default_end
    
    try:
        start_str = str(existing_row[start_col]).strip()
        end_str = str(existing_row[end_col]).strip()
        if not start_str or not end_str:
            return default_start, default_end
        # Try datetime formats first, then time-only
        for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M', '%H:%M', '%H:%M:%S']:
            try:
                start_dt = datetime.strptime(start_str[:19], fmt)
                end_dt = datetime.strptime(end_str[:19], fmt)
                if fmt in ('%H:%M', '%H:%M:%S'):
                    start_dt = datetime.combine(default_start.date(), start_dt.time())
                    end_dt = datetime.combine(default_end.date(), end_dt.time())
                return start_dt, end_dt
            except (ValueError, TypeError):
                continue
    except Exception:
        pass
    return default_start, default_end


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

if "sleep_df" not in st.session_state:
    st.session_state.sleep_df = pd.DataFrame(ws.get_all_records())

st.title("🧸 Sleep Schedule")

today = date.today()
# Default: last night 22:00 -> this morning 06:00
default_start = datetime.combine(today - timedelta(days=1), time(22, 0))
default_end = datetime.combine(today, time(6, 0))

df_records = st.session_state.sleep_df.to_dict(orient="records")
existing_row_idx = None
existing_row = None
start_col, end_col = find_sleep_columns(st.session_state.sleep_df) if not st.session_state.sleep_df.empty else (None, None)
for i, row in enumerate(df_records):
    if start_col and row.get(start_col):
        try:
            s = str(row[start_col]).strip()
            for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M', '%H:%M', '%H:%M:%S']:
                try:
                    dt = datetime.strptime(s[:19], fmt)
                    if fmt in ('%H:%M', '%H:%M:%S'):
                        dt = datetime.combine(default_start.date(), dt.time())
                    if dt.date() == default_start.date():
                        existing_row_idx = i + 2
                        existing_row = row
                        break
                    break
                except (ValueError, TypeError):
                    continue
        except Exception:
            pass
    if existing_row_idx is not None:
        break

prefill_start, prefill_end = get_prefill_datetimes(existing_row, default_start, default_end)

col1, col2 = st.columns(2)
sleep_start = col1.datetime_input("Sleep Start", value=prefill_start)
sleep_end = col2.datetime_input("Sleep End", value=prefill_end)

col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

if save_clicked:
    start_str = sleep_start.strftime("%Y-%m-%d %H:%M")
    end_str = sleep_end.strftime("%Y-%m-%d %H:%M")
    if existing_row_idx:
        ws.update(values=[[start_str, end_str]], range_name=f"A{existing_row_idx}:B{existing_row_idx}")
        st.success(f"Updated sleep log for {sleep_start.date()}.")
    else:
        ws.append_row([start_str, end_str])
        st.success(f"Added new sleep log for {sleep_start.date()}.")
    st.session_state.sleep_df = pd.DataFrame(ws.get_all_records())

if delete_clicked and existing_row_idx:
    ws.delete_rows(existing_row_idx)
    st.success("Deleted sleep log.")
    st.session_state.sleep_df = pd.DataFrame(ws.get_all_records())

if not st.session_state.sleep_df.empty:
    df = st.session_state.sleep_df.copy()
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

    # Compute sleep duration in hours (sleep_start_datetime and sleep_end_datetime are full datetimes)
    def calc_duration(row):
        start_dt = row["sleep_start_datetime"]
        end_dt = row["sleep_end_datetime"]
        if pd.isna(start_dt) or pd.isna(end_dt):
            return None
        if end_dt <= start_dt:
            end_dt = end_dt + timedelta(days=1)
        return round((end_dt - start_dt).total_seconds() / 3600, 2)

    df["Sleep Duration (hrs)"] = df.apply(calc_duration, axis=1)

    # Compute average times
    def average_time(times):
        seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in times]
        avg_seconds = sum(seconds) / len(seconds)
        h = int(avg_seconds // 3600) % 24
        m = int((avg_seconds % 3600) // 60)
        return time(h, m)

    st.write("")
    st.write("")
    header_col, col1, col2 = st.columns([2, 1, 1])
    
    with header_col:
        st.subheader("Sleep Schedule Analysis")
    
    valid_dates = df["date"].dropna()
    if valid_dates.empty:
        st.warning("No valid dates found in the data.")
        st.stop()
    
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    
    today = date.today()
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = today
        max_date = today
    
    with col1:
        start_filter = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    with col2:
        end_filter = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

    filtered_df = pd.DataFrame()
    if start_filter > end_filter:
        st.warning("⚠️ Invalid date range: Start Date cannot be after End Date.")
    else:
        filtered_df = df[(df["date"].dt.date >= start_filter) & (df["date"].dt.date <= end_filter)].copy()

    if not filtered_df.empty:
        start_times = [x.time() for x in filtered_df["sleep_start_datetime"].dropna() if hasattr(x, 'time')]
        end_times = [x.time() for x in filtered_df["sleep_end_datetime"].dropna() if hasattr(x, 'time')]
        avg_start = average_time(start_times) if start_times else time(0, 0)
        avg_end = average_time(end_times) if end_times else time(0, 0)
        avg_duration = filtered_df["Sleep Duration (hrs)"].mean()

        # Metrics
        col3, col4, col5 = st.columns([1, 1, 1])
        with col3:
            st.metric("Avg. Sleep Start", avg_start.strftime("%H:%M"))
        with col4:
            st.metric("Avg. Sleep End", avg_end.strftime("%H:%M"))
        with col5:
            st.metric("Avg. Sleep Duration (hrs)", f"{avg_duration:.2f}")

        # Line Chart
        duration_chart = (
            filtered_df[["date", "Sleep Duration (hrs)"]]
            .dropna(subset=["Sleep Duration (hrs)"])
            .sort_values("date")
            .copy()
        )
        duration_chart["date"] = pd.to_datetime(duration_chart["date"]).dt.normalize()
        duration_chart = duration_chart.reset_index(drop=True)

        if not duration_chart.empty:
            dur_min = float(duration_chart["Sleep Duration (hrs)"].min())
            dur_max = float(duration_chart["Sleep Duration (hrs)"].max())
            y_pad = max(0.5, (dur_max - dur_min) * 0.2) if dur_max > dur_min else 1.0
            y_range = [max(0.0, dur_min - y_pad), dur_max + y_pad]
        else:
            y_range = [0, 10]

        if duration_chart.empty:
            st.info("No duration data to plot for the selected date range.")
        else:
            fig = px.line(
                duration_chart,
                x="date",
                y="Sleep Duration (hrs)",
                markers=True,
                color_discrete_sequence=["#028283"],
                title="Sleep Duration Over Time",
            )
            fig.add_hline(
                y=7,
                line_dash="dash",
                line_color="#e7541e",
                annotation_text="Target: 7.0 hrs",
                annotation_position="top left",
            )
            fig.update_traces(mode="lines+markers")
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Sleep Duration (hrs)",
                xaxis=dict(
                    type="date",
                    tickformat="%b %d",
                    tickangle=0,
                    showgrid=False,
                    showline=False,
                    rangeslider_visible=False,
                ),
                yaxis=dict(
                    range=y_range,
                    showgrid=False,
                    dtick=1,
                ),
                template="plotly_white",
                margin=dict(t=50, b=50),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Interactive Table
        df_display = filtered_df.rename(columns={
            "date": "Date",
            "sleep_start_datetime": "Sleep Start",
            "sleep_end_datetime": "Sleep End"
        })
        df_display["Date"] = df_display["Date"].dt.date
        df_display["Sleep Start"] = df_display["Sleep Start"].apply(lambda t: t.strftime("%Y-%m-%d %H:%M") if pd.notna(t) and hasattr(t, 'strftime') else "")
        df_display["Sleep End"] = df_display["Sleep End"].apply(lambda t: t.strftime("%Y-%m-%d %H:%M") if pd.notna(t) and hasattr(t, 'strftime') else "")

        with st.expander("Log Entries", expanded=False):
            st.dataframe(df_display.sort_values("Date", ascending=False).drop(columns=["Date"]), width="stretch")
else:
    st.info("No sleep logs yet.")