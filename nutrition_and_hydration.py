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
ws = client.open("nutrition_and_hydration").sheet1

# Load Data
if "nutrition_df" not in st.session_state:
    st.session_state.nutrition_df = pd.DataFrame(ws.get_all_records())

st.title("🍎 Nutrition & Hydration")

today = date.today()

# Entry Form
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
    breakfast = st.text_input("Breakfast", value=prefill_breakfast)
    breakfast_image = st.file_uploader("Breakfast Photo", type=['png', 'jpg', 'jpeg'], key="breakfast_img", help="Optional: Upload a photo of your breakfast")
    dinner = st.text_input("Dinner", value=prefill_dinner)
    dinner_image = st.file_uploader("Dinner Photo", type=['png', 'jpg', 'jpeg'], key="dinner_img", help="Optional: Upload a photo of your dinner")
with col2:
    lunch = st.text_input("Lunch", value=prefill_lunch)
    lunch_image = st.file_uploader("Lunch Photo", type=['png', 'jpg', 'jpeg'], key="lunch_img", help="Optional: Upload a photo of your lunch")
    snacks = st.text_input("Snacks", value=prefill_snacks)
    snacks_image = st.file_uploader("Snacks Photo", type=['png', 'jpg', 'jpeg'], key="snacks_img", help="Optional: Upload a photo of your snacks")

col3, col4 = st.columns(2)
with col3:
    supplements = st.text_input("Supplements", value=prefill_supplements)
with col4:
    water_ml = st.number_input("Water (ml)", min_value=0, step=100, value=int(prefill_water))

# Action Buttons
col_save, col_delete = st.columns([1, 1])
with col_save:
    save_clicked = st.button("☁️ Save")
with col_delete:
    delete_clicked = st.button("🗑️ Delete", disabled=(existing_row_idx is None))

# Helper function to process image to base64
import base64
import io
from PIL import Image

def process_image_to_base64(image_file):
    if image_file is None:
        return ""
    
    try:
        # Compress image to reduce size
        img = Image.open(image_file)
        
        # Start with smaller size for Google Sheets compatibility
        max_size = 300  # Reduced from 800
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Convert to base64 with lower quality
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60, optimize=True)  # Reduced from 85
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Check if still too large and compress further if needed
        max_chars = 45000  # Leave some buffer under 50k limit
        if len(img_base64) > max_chars:
            # Further reduce size
            max_size = 200
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=40, optimize=True)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # If still too large, return empty string
        if len(img_base64) > max_chars:
            st.warning(f"Image too large to save. Please use a smaller image.")
            return ""
        
        return img_base64
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return ""

# Handle Save/Delete
if save_clicked:
    try:
        # Process images to base64
        breakfast_img_b64 = process_image_to_base64(breakfast_image)
        lunch_img_b64 = process_image_to_base64(lunch_image)
        dinner_img_b64 = process_image_to_base64(dinner_image)
        snacks_img_b64 = process_image_to_base64(snacks_image)
        
        # Prepare data row
        data_row = [str(entry_date), breakfast, lunch, dinner, snacks, supplements, int(water_ml),
                   breakfast_img_b64, lunch_img_b64, dinner_img_b64, snacks_img_b64]
        
        if existing_row_idx:
            # Update existing row - need to handle variable number of columns
            ws.update(values=[data_row[1:]], range_name=f"B{existing_row_idx}")
            st.success(f"Updated nutrition log for {entry_date}.")
        else:
            ws.append_row(data_row)
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

# Analytics
if not st.session_state.nutrition_df.empty:
    df = st.session_state.nutrition_df.copy()
    df["date"] = pd.to_datetime(df["date"])

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

    # Results Section
    st.write("")
    st.write("")
    header_col, filter_col1, filter_col2 = st.columns([2, 1, 1])
    
    with header_col:
        st.subheader("Nutrition & Hydration Analysis")
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
        # Helper function to display image from base64
        def display_base64_image(base64_str, width=150):
            if base64_str and str(base64_str).strip():
                try:
                    img_data = base64.b64decode(base64_str)
                    st.image(img_data, width=width)
                except:
                    st.write("Invalid image")
            else:
                st.write("No image")
        
        # Display meals with images
        for _, row in filtered_df.sort_values("date", ascending=False).iterrows():
            meal_date = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
            
            with st.expander(f"🍽️ {meal_date}", expanded=False):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**Breakfast**")
                    st.write(row.get("breakfast", ""))
                    if "breakfast_image" in row and row["breakfast_image"]:
                        display_base64_image(row["breakfast_image"])
                    
                    st.write("**Dinner**")
                    st.write(row.get("dinner", ""))
                    if "dinner_image" in row and row["dinner_image"]:
                        display_base64_image(row["dinner_image"])
                
                with col2:
                    st.write("**Lunch**")
                    st.write(row.get("lunch", ""))
                    if "lunch_image" in row and row["lunch_image"]:
                        display_base64_image(row["lunch_image"])
                    
                    st.write("**Snacks**")
                    st.write(row.get("snacks", ""))
                    if "snacks_image" in row and row["snacks_image"]:
                        display_base64_image(row["snacks_image"])
                
                st.write("**Supplements:**", row.get("supplements", ""))
                st.write("**Water:**", row.get("water_ml", 0), "ml")
    else:
        st.info("No records in selected date range.")
else:
    st.info("No nutrition logs yet.")