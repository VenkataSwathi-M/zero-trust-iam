import streamlit as st
from iam_core.events.security_event_listener import SecurityEventListener

listener = SecurityEventListener()

st.set_page_config(page_title="Attack Simulator", layout="wide")
st.title("⚠️ Attack Simulation Console")

agent = st.text_input("Target Agent ID", "user-123")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔓 Brute Force Attack"):
        res = listener.handle_event("auth_failed")
        st.error(res)

with col2:
    if st.button("🧠 Anomaly Detected"):
        res = listener.handle_event("anomaly_detected")
        st.warning(res)

with col3:
    if st.button("💥 Session Abuse"):
        res = listener.handle_event("session_abuse")
        st.error(res)