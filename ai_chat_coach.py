import streamlit as st

st.title("💬 Coach Chat")

st.info("Chat with your AI wellness coach. Coming soon.")

st.text_area("Message", placeholder="Ask your coach about your habits, goals, or insights...", key="chat_input", height=100)
if st.button("Send"):
    st.caption("Chat will be available in a future update.")
