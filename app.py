import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")
st.image("images/BeWell360-lg.svg", width=300)

# ---------------- Data Folder ----------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------- Footer ----------------
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;'>
        <span style='font-weight:bold;'>Powered by</span>
        <img src='images/Oranlytix-lg.svg' width='150'>
    </div>
    <div style='text-align:center; font-size:12px; color:gray; margin-top:5px;'>
        © 2025 BeWell360. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)