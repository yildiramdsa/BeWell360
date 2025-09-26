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

if "vision_board_df" not in st.session_state:
    st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())

st.title("🎨 Vision Board")

if not st.session_state.vision_board_df.empty:
    df = st.session_state.vision_board_df.copy()
    
    image_col = None
    for col in df.columns:
        if col.lower() in ['image', 'picture', 'photo']:
            image_col = col
            break
    
    if image_col is None and len(df.columns) > 0:
        image_col = df.columns[0]
    
    if image_col is None:
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
                    image_data = row.get(image_col, '')
                    
                    if image_data:
                        with col:
                            try:
                                image_bytes = base64.b64decode(image_data)
                                image = Image.open(BytesIO(image_bytes))
                                st.image(image, use_column_width=True)
                                
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
                                                        image_bytes = edit_image.read()
                                                        image_data_to_save = base64.b64encode(image_bytes).decode()
                                                        ws.update(values=[[image_data_to_save]], 
                                                                 range_name=f"A{idx+2}")
                                                        st.success("Image updated successfully!")
                                                        st.session_state[f"editing_{idx}"] = False
                                                        st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                                                        st.rerun()
                                                    else:
                                                        st.warning("Please select a new image.")
                                                except Exception as e:
                                                    st.error(f"Error updating image: {str(e)}")
                                        
                                        with edit_cancel_col:
                                            if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                                                st.session_state[f"editing_{idx}"] = False
                                                st.rerun()
                            except:
                                st.write("Image could not be displayed")
        
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
                        image_bytes = new_image.read()
                        image_data_to_save = base64.b64encode(image_bytes).decode()
                        
                        ws.append_row([image_data_to_save])
                        st.success("Image added to your vision board!")
                        st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding image: {str(e)}")
                else:
                    st.error("Please select an image to upload.")
        
        total_items = len([row for _, row in df.iterrows() if str(row.get(image_col, '')).strip()])
        
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
                    image_bytes = new_image.read()
                    image_data_to_save = base64.b64encode(image_bytes).decode()
                    
                    ws.append_row([image_data_to_save])
                    st.success("Image added to your vision board!")
                    st.session_state.vision_board_df = pd.DataFrame(ws.get_all_records())
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding image: {str(e)}")
            else:
                st.error("Please select an image to upload.")
        
        if st.button("☁️ Save", help="Close management section"):
            st.session_state["show_management"] = False
            st.rerun()