import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, time, datetime, timedelta
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
ws = client.open("sleep_schedule").sheet1

# ---------------- Load Data ----------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(ws.get_all_records())

st.title("🧸 Sleep Schedule")

# ---------------- Default Values ----------------
today = date.today()
default_start = time(22, 0)
default_end = time(6, 0)

# ---------------- Initialize form state ----------------
st.session_state.setdefault("entry_date", today)
st.session_state.setdefault("sleep_start", default_start)
st.session_state.setdefault("sleep_end", default_end)

# ---------------- Sleep Entry ----------------
entry_date = st.date_input("Date", st.session_state.entry_date, key="entry_date")

# ---------------- Prefill times if entry exists ----------------
df = st.session_state.df.copy()
df["date"] = pd.to_datetime(df["date"]).dt.date

existing_entry = df[df["date"] == entry_date]
prefill_start = datetime.strptime(existing_entry.iloc[0]["sleep_start"], "%H:%M").time() if not existing_entry.empty else st.session_state.sleep_start
prefill_end = datetime.strptime(existing_entry.iloc[0]["sleep_end"], "%H:%M").time() if not existing_entry.empty else st.session_state.sleep_end

col1, col2 = st.columns(2)
sleep_start = col1.time_input("Sleep Start", value=prefill_start, key="sleep_start")
sleep_end = col2.time_input("Sleep End", value=prefill_end, key="sleep_end")

# ---------------- Action Buttons ----------------
col_save, col_delete = st.columns([1, 1])
save_label = "☁️ Update" if not existing_entry.empty else "☁️ Save"
with col_save: save_clicked = st.button(save_label)
with col_delete: delete_clicked = st.button("🗑️ Delete", disabled=existing_entry.empty)

# ---------------- Handle Save/Delete ----------------
if save_clicked:
    start_str, end_str = sleep_start.strftime("%H:%M"), sleep_end.strftime("%H:%M")
    if not existing_entry.empty:
        row_idx = df.index[df["date"] == entry_date][0] + 2
        ws.update(values=[[start_str, end_str]], range_name=f"B{row_idx}:C{row_idx}")
        st.success(f"☁️ Updated sleep log for {entry_date}")
    else:
        ws.append_row([str(entry_date), start_str, end_str])
        st.success(f"☁️ Added new sleep log for {entry_date}")
    st.session_state.df = pd.DataFrame(ws.get_all_records())

if delete_clicked and not existing_entry.empty:
    row_idx = df.index[df["date"] == entry_date][0] + 2
    ws.delete_rows(row_idx)
    st.success(f"🗑️ Deleted sleep log for {entry_date}")
    st.session_state.df = pd.DataFrame(ws.get_all_records())
    st.session_state.entry_date = today
    st.session_state.sleep_start = default_start
    st.session_state.sleep_end = default_end

# ---------------- Analytics ----------------
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["sleep_start"] = pd.to_datetime(df["sleep_start"], format="%H:%M").dt.time
    df["sleep_end"] = pd.to_datetime(df["sleep_end"], format="%H:%M").dt.time

    # Sleep Duration
    df["Sleep Duration (hrs)"] = df.apply(lambda r: ((datetime.combine(r["date"], r["sleep_end"]) - datetime.combine(r["date"], r["sleep_start"])).total_seconds()/3600) % 24, axis=1)
    df["Sleep Duration (hrs)"] = df["Sleep Duration (hrs)"].apply(lambda x: x if x > 0 else x+24)

    # Average times
    def avg_time(times): 
        total_sec = sum(t.hour*3600 + t.minute*60 for t in times)
        avg_sec = total_sec / len(times)
        return time(int(avg_sec//3600)%24, int((avg_sec%3600)//60))

    avg_start = avg_time(df["sleep_start"])
    avg_end = avg_time(df["sleep_end"])

    # Date filters
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    start_filter = col1.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date, key="start_filter")
    end_filter = col2.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date, key="end_filter")
    filtered_df = df[(df["date"].dt.date >= start_filter) & (df["date"].dt.date <= end_filter)] if start_filter <= end_filter else pd.DataFrame()

    # Metrics
    col3.metric("Avg. Sleep Start", avg_start.strftime("%H:%M"))
    col4.metric("Avg. Sleep End", avg_end.strftime("%H:%M"))
    col5.metric("Avg. Sleep Duration (hrs)", f"{df['Sleep Duration (hrs)'].mean():.2f}")

    if start_filter > end_filter: st.warning("⚠️ Start Date cannot be after End Date.")

    if not filtered_df.empty:
        # Line chart
        fig = px.line(filtered_df, x="date", y="Sleep Duration (hrs)", markers=True, color_discrete_sequence=["#028283"])
        fig.add_hline(y=7, line_dash="dash", line_color="#e7541e", annotation_text="Target Sleep (7 hrs)", annotation_position="top left")
        fig.update_layout(xaxis_title="Date", yaxis_title="Sleep Duration (hrs)", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # Dataframe display
        df_display = filtered_df.rename(columns={"date":"Date","sleep_start":"Sleep Start","sleep_end":"Sleep End"})
        df_display["Date"] = df_display["Date"].dt.date
        df_display["Sleep Start"] = df_display["Sleep Start"].apply(lambda t: t.strftime("%H:%M"))
        df_display["Sleep End"] = df_display["Sleep End"].apply(lambda t: t.strftime("%H:%M"))
        st.dataframe(df_display.sort_values("Date", ascending=False), width='stretch')

else:
    st.info("No sleep logs yet.")