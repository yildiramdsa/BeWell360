import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import plotly.express as px

# ---------------- Helper Functions ----------------
def find_body_composition_columns(df):
    """Find body composition columns in the dataframe."""
    weight_col = None
    body_fat_col = None
    muscle_col = None
    
    # Check for expected column names first
    expected_columns = {
        'weight': ['weight_lb', 'weight', 'weight_pounds'],
        'body_fat': ['body_fat_percent', 'body_fat', 'bodyfat_percent', 'fat_percent'],
        'muscle': ['skeletal_muscle_percent', 'muscle_percent', 'muscle', 'skeletal_muscle']
    }
    
    # Find weight column
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['weight', 'lb', 'pound']):
            weight_col = col
            break
    
    # Find body fat column
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['fat', 'bodyfat']):
            body_fat_col = col
            break
    
    # Find muscle column
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['muscle', 'skeletal']):
            muscle_col = col
            break
    
    # Fallback to positional columns if names not found
    if not weight_col and len(df.columns) > 1:
        weight_col = df.columns[1]
    if not body_fat_col and len(df.columns) > 2:
        body_fat_col = df.columns[2]
    if not muscle_col and len(df.columns) > 3:
        muscle_col = df.columns[3]
    
    return weight_col, body_fat_col, muscle_col


def clean_body_composition_data(df, weight_col, body_fat_col, muscle_col):
    """Clean and parse body composition data from the dataframe."""
    try:
        # Clean the data first - remove any empty or invalid values
        df_clean = df.dropna(subset=[weight_col, body_fat_col, muscle_col])
        
        # Convert to numeric with error handling
        df_clean[weight_col] = pd.to_numeric(df_clean[weight_col], errors='coerce')
        df_clean[body_fat_col] = pd.to_numeric(df_clean[body_fat_col], errors='coerce')
        df_clean[muscle_col] = pd.to_numeric(df_clean[muscle_col], errors='coerce')
        
        # Remove rows where conversion failed
        df_clean = df_clean.dropna(subset=[weight_col, body_fat_col, muscle_col])
        
        # Validate reasonable ranges
        df_clean = df_clean[
            (df_clean[weight_col] > 0) & (df_clean[weight_col] < 1000) &  # Reasonable weight range
            (df_clean[body_fat_col] >= 0) & (df_clean[body_fat_col] <= 100) &  # Body fat percentage
            (df_clean[muscle_col] >= 0) & (df_clean[muscle_col] <= 100)  # Muscle percentage
        ]
        
        if df_clean.empty:
            return None
        
        # Rename columns to standard names
        df_clean = df_clean.rename(columns={
            weight_col: 'weight_lb',
            body_fat_col: 'body_fat_percent',
            muscle_col: 'skeletal_muscle_percent'
        })
        
        return df_clean
        
    except Exception as e:
        st.error(f"Error processing body composition data: {str(e)}")
        return None


def get_prefill_values(existing_row):
    """Get prefill values from existing row data."""
    if not existing_row:
        return 0.0, 0.0, 0.0
    
    # Find columns in existing row
    weight_col, body_fat_col, muscle_col = find_body_composition_columns(pd.DataFrame([existing_row]))
    
    try:
        weight_val = float(existing_row.get(weight_col, 0)) if weight_col and existing_row.get(weight_col) else 0.0
        body_fat_val = float(existing_row.get(body_fat_col, 0)) if body_fat_col and existing_row.get(body_fat_col) else 0.0
        muscle_val = float(existing_row.get(muscle_col, 0)) if muscle_col and existing_row.get(muscle_col) else 0.0
        
        return weight_val, body_fat_val, muscle_val
    except:
        return 0.0, 0.0, 0.0


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
ws = client.open("body_composition").sheet1

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
        existing_row_idx = i + 2
        existing_row = row
        break

# Prefill values
prefill_weight, prefill_bodyfat, prefill_muscle = get_prefill_values(existing_row)

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
    try:
        # Validate input values
        if weight_lb <= 0 or body_fat < 0 or body_fat > 100 or muscle < 0 or muscle > 100:
            st.error("Please enter valid values: Weight > 0, Body Fat 0-100%, Muscle 0-100%")
        else:
            if existing_row_idx:
                ws.update(values=[[weight_lb, body_fat, muscle]], range_name=f"B{existing_row_idx}:D{existing_row_idx}")
                st.success(f"💾 Updated body composition log for {entry_date}")
            else:
                ws.append_row([str(entry_date), weight_lb, body_fat, muscle])
                st.success(f"✅ Added new body composition log for {entry_date}")
            st.session_state.df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

if delete_clicked and existing_row_idx:
    try:
        ws.delete_rows(existing_row_idx)
        st.success(f"🗑️ Deleted body composition log for {entry_date}")
        st.session_state.df = pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")

# ---------------- Analytics ----------------
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    # Find body composition columns
    weight_col, body_fat_col, muscle_col = find_body_composition_columns(df)
    
    if not weight_col or not body_fat_col or not muscle_col:
        st.error("Could not find required body composition columns in the data.")
        st.stop()
    
    # Clean and parse the data
    df_clean = clean_body_composition_data(df, weight_col, body_fat_col, muscle_col)
    
    if df_clean is None:
        st.warning("No valid body composition data found in the selected columns.")
        st.stop()
    
    df = df_clean

    # ---------------- Date Filter (same line) ----------------
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
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
        # ---------------- Metrics (same line) ----------------
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Avg. Weight (lb)", f"{filtered_df['weight_lb'].mean():.1f}")
        with metric_col2:
            st.metric("Avg. Body Fat (%)", f"{filtered_df['body_fat_percent'].mean():.1f}")
        with metric_col3:
            st.metric("Avg. Muscle (%)", f"{filtered_df['skeletal_muscle_percent'].mean():.1f}")

        st.subheader("📊 Trends")

        # Weight trend
        fig_wt = px.line(
            filtered_df.sort_values("date"),
            x="date",
            y="weight_lb",
            markers=True,
            color_discrete_sequence=["#028283"]
        )
        fig_wt.add_hline(
            y=filtered_df["weight_lb"].mean(),
            line_dash="dash",
            line_color="#e7541e",
            annotation_text="Avg. Weight",
            annotation_position="top left"
        )
        fig_wt.update_layout(
            xaxis_title="Date",
            yaxis_title="Weight (lb)",
            xaxis=dict(tickformat="%d %b", showgrid=False, showline=False),
            yaxis=dict(showgrid=False),
            template="plotly_white"
        )
        st.plotly_chart(fig_wt, use_container_width=True)

        # Body fat & muscle trend
        fig_bf = px.line(
            filtered_df.sort_values("date"),
            x="date",
            y=["body_fat_percent", "skeletal_muscle_percent"],
            markers=True,
            color_discrete_sequence=["#e7541e", "#028283"]
        )
        fig_bf.update_layout(
            xaxis_title="Date",
            yaxis_title="Percentage (%)",
            xaxis=dict(tickformat="%d %b", showgrid=False, showline=False),
            yaxis=dict(showgrid=False),
            template="plotly_white",
            legend_title_text=""
        )
        st.plotly_chart(fig_bf, use_container_width=True)

        # ---------------- Interactive Table ----------------
        df_display = filtered_df.rename(columns={
            "date": "Date",
            "weight_lb": "Weight (lb)",
            "body_fat_percent": "Body Fat (%)",
            "skeletal_muscle_percent": "Muscle (%)"
        })
        df_display["Date"] = df_display["Date"].dt.date
        st.dataframe(df_display.sort_values("Date", ascending=False), width="stretch")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No body composition logs yet.")