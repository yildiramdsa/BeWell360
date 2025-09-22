import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# ---------------- Page Config ----------------
st.set_page_config(page_title="BeWell360", layout="wide")
st.image("images/BeWell360-lg.png", width=200)

# ---------------- Data Folder ----------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ---------------- Footer ----------------
st.markdown("---")
col1, col2 = st.columns([1, 0.2])
with col1:
    st.markdown("Powered by")
with col2:
    st.image("images/Oranlytix-lg.png", width=50)