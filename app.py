import streamlit as st
import base64
import os

st.set_page_config(page_title="BeWell360", layout="wide")

# Header Logo
with open("images/BeWell360-lg.svg", "rb") as f:
    encoded_svg = base64.b64encode(f.read()).decode()

st.markdown(
    f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{encoded_svg}" width="250"></div>',
    unsafe_allow_html=True
)

st.title("Welcome to BeWell360")
st.markdown("Select a page from the sidebar to begin your holistic wellness journey!")

# Footer
with open("images/Oranlytix-lg.svg", "rb") as f:
    encoded_svg = base64.b64encode(f.read()).decode()

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align:center;">
        <span style="font-size:10px; color:gray;">Powered by</span>
        <img src="data:image/svg+xml;base64,{encoded_svg}" width="75">
        <div style="font-size:10px; color:gray;">© 2025 BeWell360. All rights reserved.</div>
    </div>
    """,
    unsafe_allow_html=True
)