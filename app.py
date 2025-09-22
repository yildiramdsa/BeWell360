import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import base64

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")
with open("images/BeWell360-lg.svg", "rb") as f:
    svg_bytes = f.read()
    encoded_svg = base64.b64encode(svg_bytes).decode()
st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/svg+xml;base64,{encoded_svg}" width="400">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- Data Folder ----------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------- Footer ----------------
with open("images/Oranlytix-lg.svg", "rb") as f:
    svg_bytes = f.read()
    encoded_svg = base64.b64encode(svg_bytes).decode()
footer_html = f"""
<div style="text-align:center;">
    <span style="font-weight:bold; font-size:12px;">Powered by</span>
    <img src="data:image/svg+xml;base64,{encoded_svg}" width="100">
    <div style="font-size:12px; color:gray; margin-top:5px;">© 2025 BeWell360. All rights reserved.</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)