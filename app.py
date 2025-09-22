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
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<span style='font-weight:bold; font-size:12px;'>Powered by</span>", unsafe_allow_html=True)
    st.image("images/Oranlytix-lg.png", width=100)
    st.markdown("<div style='font-size:12px; color:gray;'>© 2025 BeWell360. All rights reserved.</div>", unsafe_allow_html=True)

