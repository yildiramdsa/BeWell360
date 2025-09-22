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
st.markdown("---")
st.markdown(
    """
    <p style='display: flex; align-items: center;'>
        <span style='margin-right:10px;'>Powered by</span>
        <img src='images/Oranlytix-lg.svg' width='100'>
    </p>
    """,
    unsafe_allow_html=True
)