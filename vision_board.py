import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
from io import BytesIO
from PIL import Image
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

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

# Google Drive service for file uploads
drive_service = build('drive', 'v3', credentials=creds)

def upload_image_to_drive(image_file, filename):
    """Upload image to Google Drive and return file ID."""
    try:
        # Create file metadata
        file_metadata = {
            'name': filename,
            'parents': []  # Upload to root folder
        }
        
        # Create media upload
        media = MediaIoBaseUpload(
            BytesIO(image_file.read()),
            mimetype=image_file.type,
            resumable=True
        )
        
        # Upload file
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except Exception as e:
        st.error(f"Error uploading to Drive: {str(e)}")
        return None

def get_image_from_drive(file_id):
    """Get image from Google Drive by file ID."""
    try:
        # Get file metadata
        file = drive_service.files().get(fileId=file_id).execute()
        
        # Download file content
        request = drive_service.files().get_media(fileId=file_id)
        file_content = BytesIO()
        
        # Download in chunks
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_content.seek(0)
        return Image.open(file_content)
    except Exception as e:
        st.error(f"Error loading image from Drive: {str(e)}")
        return None

if "vision_board_df" not in st.session_state:
    st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())

st.title("🎨 Vision Board")

if not st.session_state.vision_board_df.empty:
    df = st.session_state.vision_board_df.copy()
    
    # Debug: Show what's in the dataframe
    st.write("Debug - DataFrame columns:", df.columns.tolist())
    st.write("Debug - DataFrame shape:", df.shape)
    st.write("Debug - First few rows:", df.head())
    
    file_id_col = None
    for col in df.columns:
        if col.lower() in ['file_id', 'image_id', 'drive_id']:
            file_id_col = col
            break
    
    if file_id_col is None and len(df.columns) > 0:
        file_id_col = df.columns[0]
    
    st.write(f"Debug - Using column: {file_id_col}")
    
    if file_id_col is None:
        st.error("No data found in the Google Sheet. Please add some images.")
    else:
        # Display images in a grid
        images_per_row = 3
        for i in range(0, len(df), images_per_row):
            cols = st.columns(images_per_row)
            for j, col in enumerate(cols):
                if i + j < len(df):
                    idx = i + j
                    row = df.iloc[idx]
                    file_id = row.get(file_id_col, '')
                    
                    if file_id:
                        with col:
                            st.write(f"Debug - File ID: {file_id}")
                            try:
                                image = get_image_from_drive(file_id)
                                if image:
                                    st.image(image, use_column_width=True)
                                else:
                                    st.write("Could not load image from Drive")
                                
                                if st.session_state.get("show_management", False):
                                    col_edit, col_delete = st.columns([1, 1])
                                    with col_edit:
                                        if st.button("✏️", key=f"edit_{idx}", help="Edit", use_container_width=True):
                                            st.session_state[f"editing_{idx}"] = True
                                    with col_delete:
                                        if st.button("🗑️", key=f"delete_{idx}", help="Delete", use_container_width=True):
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
                                                        new_file_id = upload_image_to_drive(edit_image, f"vision_board_{idx}_{edit_image.name}")
                                                        if new_file_id:
                                                            ws.update(values=[[new_file_id]], 
                                                                     range_name=f"A{idx+2}")
                                                            st.success("Image updated successfully!")
                                                            st.session_state[f"editing_{idx}"] = False
                                                            st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to upload new image.")
                                                    else:
                                                        st.warning("Please select a new image.")
                                                except Exception as e:
                                                    st.error(f"Error updating image: {str(e)}")
                                        
                                        with edit_cancel_col:
                                            if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                                                st.session_state[f"editing_{idx}"] = False
                                                st.rerun()
                            except Exception as e:
                                st.write(f"Image could not be displayed: {str(e)}")
        
        if st.session_state.get("show_management", False):
            st.subheader("Add New Image")
            new_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], key="new_image_input")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                add_clicked = st.button("➕ Add Image", key="add_new_image", help="Add image to vision board")
            with col2:
                if st.button("🗑️ Clear", key="clear_new_image", help="Clear"):
                    st.rerun()
            
            if add_clicked:
                if new_image:
                    try:
                        file_id = upload_image_to_drive(new_image, f"vision_board_{new_image.name}")
                        if file_id:
                            ws.append_row([file_id])
                            st.success("Image added to your vision board!")
                            st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                            st.rerun()
                        else:
                            st.error("Failed to upload image to Drive.")
                    except Exception as e:
                        st.error(f"Error adding image: {str(e)}")
                else:
                    st.error("Please select an image to upload.")
        
        total_items = len([row for _, row in df.iterrows() if str(row.get(file_id_col, '')).strip()])
        
        st.caption(f"Total images: {total_items}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("⚙️ Manage Vision Board", help="Edit or delete images", disabled=st.session_state.get("show_management", False)):
                st.session_state["show_management"] = True
                st.rerun()
        
        with col2:
            if st.session_state.get("show_management", False):
                if st.button("☁️ Save", help="Close management section"):
                    st.session_state["show_management"] = False
                    st.rerun()

else:
    st.info("No images yet. Click 'Manage Vision Board' below to add your first image!")
    
    if st.button("⚙️ Manage Vision Board", help="Add your first image"):
        st.session_state["show_management"] = True
        st.rerun()
    
    if st.session_state.get("show_management", False):
        st.subheader("Add New Image")
        new_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], key="new_image_input_empty")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            add_clicked = st.button("➕ Add Image", key="add_new_image_empty", help="Add image to vision board")
        with col2:
            if st.button("🗑️ Clear", key="clear_new_image_empty", help="Clear"):
                st.rerun()
        
        if add_clicked:
            if new_image:
                try:
                    file_id = upload_image_to_drive(new_image, f"vision_board_{new_image.name}")
                    if file_id:
                        ws.append_row([file_id])
                        st.success("Image added to your vision board!")
                        st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    else:
                        st.error("Failed to upload image to Drive.")
                except Exception as e:
                    st.error(f"Error adding image: {str(e)}")
            else:
                st.error("Please select an image to upload.")
        
        if st.button("☁️ Save", help="Close management section"):
            st.session_state["show_management"] = False
            st.rerun()