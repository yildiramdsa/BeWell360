import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
from io import BytesIO
from PIL import Image


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
client = gspread.authorize(creds)
ws = client.open("vision_board").sheet1

def compress_image(image_file, max_size_kb=30):
    try:
        image = Image.open(image_file)
        
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        target_size = max_size_kb * 1024
        
        for quality in range(95, 10, -5):
            output = BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            
            if output.tell() <= target_size:
                output.seek(0)
                return base64.b64encode(output.read()).decode()
        
        for scale in [0.8, 0.6, 0.4, 0.2]:
            new_size = (int(image.width * scale), int(image.height * scale))
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            resized.save(output, format='JPEG', quality=70, optimize=True)
            
            if output.tell() <= target_size:
                output.seek(0)
                return base64.b64encode(output.read()).decode()
        
        return None
    except Exception as e:
        st.error(f"Error compressing image: {str(e)}")
        return None

def get_image_from_base64(image_data):
    try:
        image_bytes = base64.b64decode(image_data)
        return Image.open(BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Error loading image from base64: {str(e)}")
        return None

def upload_pending_images():
    if st.session_state.get("pending_images"):
        uploaded_count = 0
        for new_image in st.session_state["pending_images"]:
            if new_image not in st.session_state.get("uploaded_files", []):
                try:
                    compressed_data = compress_image(new_image)
                    if compressed_data:
                        ws.append_row([compressed_data])
                        uploaded_count += 1
                        
                        if "uploaded_files" not in st.session_state:
                            st.session_state.uploaded_files = []
                        st.session_state.uploaded_files.append(new_image)
                    else:
                        st.error(f"Failed to compress {new_image.name}")
                except Exception as e:
                    st.error(f"Error adding {new_image.name}: {str(e)}")
        
        if uploaded_count > 0:
            st.success(f"{uploaded_count} image(s) added to your vision board!")
            st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
            return True
    return False

if "vision_board_df" not in st.session_state:
    st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())

df = st.session_state.vision_board_df.copy()

st.title("🎨 Vision Board")

if not df.empty:
    image_col = None
    for col in df.columns:
        if col.lower() in ['image', 'image_data', 'picture', 'photo', 'file_id']:
            image_col = col
            break
    
    if image_col is None and len(df.columns) > 0:
        image_col = df.columns[0]
    
    if image_col is None:
        st.error("No data found in the Google Sheet. Please add some images.")
    else:
        images_per_row = 3
        for i in range(0, len(df), images_per_row):
            cols = st.columns(images_per_row)
            for j, col in enumerate(cols):
                if i + j < len(df):
                    idx = i + j
                    row = df.iloc[idx]
                    image_data = row.get(image_col, '')
                    
                    if image_data:
                        with col:
                            try:
                                image = get_image_from_base64(image_data)
                                if image:
                                    st.image(image, width='stretch')
                                else:
                                    st.error("Could not load image")
                                
                                if st.session_state.get("show_management", False):
                                    col_edit, col_delete = st.columns([1, 1])
                                    with col_edit:
                                        if st.button("✏️", key=f"edit_{idx}", help="Edit", width='stretch'):
                                            st.session_state[f"editing_{idx}"] = True
                                    with col_delete:
                                        if st.button("🗑️", key=f"delete_{idx}", help="Delete", width='stretch'):
                                            try:
                                                ws.delete_rows(idx + 2)
                                                st.success("Image deleted from vision board!")
                                                st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error deleting image: {str(e)}")
                                
                                if st.session_state.get(f"editing_{idx}", False):
                                    with st.expander(f"Edit Image {idx + 1}", expanded=True):
                                        edit_image = st.file_uploader("Upload New Image", type=['png', 'jpg', 'jpeg'], key=f"edit_image_{idx}")
                                        
                                        edit_save_col, edit_cancel_col = st.columns([1, 1])
                                        with edit_save_col:
                                            if st.button("☁️ Save Changes", key=f"save_edit_{idx}"):
                                                try:
                                                    if edit_image:
                                                        compressed_data = compress_image(edit_image)
                                                        if compressed_data:
                                                            ws.update(values=[[compressed_data]], 
                                                                     range_name=f"A{idx+2}")
                                                            st.success("Image updated successfully!")
                                                            st.session_state[f"editing_{idx}"] = False
                                                            st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to compress image.")
                                                    else:
                                                        st.warning("Please select a new image.")
                                                except Exception as e:
                                                    st.error(f"Error updating image: {str(e)}")
                                        
                                        with edit_cancel_col:
                                            if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                                                st.session_state[f"editing_{idx}"] = False
                                                st.rerun()
                            except Exception as e:
                                st.error(f"Image could not be displayed: {str(e)}")
        
        if st.session_state.get("show_management", False):
            new_images = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], key="new_image_input", accept_multiple_files=True)
            
            if new_images:
                st.session_state["pending_images"] = new_images
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("⚙️ Manage Vision Board", help="Edit or delete images", disabled=st.session_state.get("show_management", False)):
                st.session_state["show_management"] = True
                st.rerun()
        
        with col2:
            if st.session_state.get("show_management", False):
                if st.button("☁️ Save", help="Save and close management section"):
                    if upload_pending_images():
                        st.rerun()
                    
                    st.session_state["show_management"] = False
                    st.session_state.uploaded_files = []
                    st.session_state["pending_images"] = []
                    st.rerun()

else:
    st.info("No images yet. Click 'Manage Vision Board' below to add your first image!")
    
    if st.button("⚙️ Manage Vision Board", help="Add your first image"):
        st.session_state["show_management"] = True
        st.rerun()
    
    if st.session_state.get("show_management", False):
        new_images = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], key="new_image_input_empty", accept_multiple_files=True)
        
        if new_images:
            st.session_state["pending_images"] = new_images
        
        if st.button("☁️ Save", help="Save and close management section"):
            if upload_pending_images():
                st.rerun()
            
            st.session_state["show_management"] = False
            st.session_state.uploaded_files = []
            st.session_state["pending_images"] = []
            st.rerun()