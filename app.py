import streamlit as st
import os
import base64

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")

# ---------------- Header Logo ----------------
logo_path = "images/BeWell360-lg.svg"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        svg_bytes = f.read()
        encoded_svg = base64.b64encode(svg_bytes).decode()
    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="data:image/svg+xml;base64,{encoded_svg}" width="250">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("BeWell360")

# ---------------- Main Page Content ----------------
st.title("Welcome to BeWell360")
st.markdown(
    "Select a page from the sidebar to begin your holistic wellness journey."
)

# ---------------- Data Folder ----------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------- Footer ----------------
oranlytix_logo_path = "images/Oranlytix-lg.svg"
if os.path.exists(oranlytix_logo_path):
    with open(oranlytix_logo_path, "rb") as f:
        svg_bytes = f.read()
        encoded_svg = base64.b64encode(svg_bytes).decode()

    st.markdown("<hr>", unsafe_allow_html=True)
    footer_html = f"""
    <div style="text-align:center;">
        <span style="font-size:10px; color:gray;">Powered by</span>
        <img src="data:image/svg+xml;base64,{encoded_svg}" width="75">
        <div style="font-size:10px; color:gray;">© 2025 BeWell360. All rights reserved.</div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)