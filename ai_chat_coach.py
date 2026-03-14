import streamlit as st

st.title("💬 AI Coach Chat")

st.info("Chat with your AI wellness coach. Coming soon.")

# Placeholder for future chat interface
st.text_area("Message", placeholder="Ask your coach about your habits, goals, or insights...", key="chat_input", height=100)
if st.button("Send"):
    st.caption("AI Coach chat will be available in a future update.")
