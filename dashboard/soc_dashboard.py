import streamlit as st
import pandas as pd

from iam_core.trust.trust_store import get_trust_history
from iam_core.enforcement.enforcement_dispatcher import ENFORCEMENT_LOG
from iam_core.events.security_event_listener import SecurityEventListener

listener = SecurityEventListener()

st.set_page_config(
    page_title="Zero Trust SOC Dashboard",
    layout="wide"
)

st.title("🛡️ Zero Trust IAM – SOC Command Center")

# --------------------------------------------------
# 🔍 Agent Selection
# --------------------------------------------------
agent_id = st.text_input("Agent / Identity ID", "user-123")

# --------------------------------------------------
# 📊 TRUST SCORE GRAPH
# --------------------------------------------------
st.subheader("📈 Live Trust Score Evolution")

trust_history = get_trust_history(agent_id)

if trust_history:
    df_trust = pd.DataFrame(trust_history)
    df_trust["timestamp"] = pd.to_datetime(df_trust["timestamp"])
    st.line_chart(df_trust.set_index("timestamp")["trust"], height=300)
else:
    st.info("No trust history available.")

# --------------------------------------------------
# ⚠️ RISK + ENFORCEMENT VIEW
# --------------------------------------------------
st.subheader("⚠️ Latest Enforcement Decisions")

if ENFORCEMENT_LOG:
    df_enforce = pd.DataFrame(ENFORCEMENT_LOG[-10:])
    st.dataframe(df_enforce, use_container_width=True)
else:
    st.info("No enforcement actions yet.")

# --------------------------------------------------
# 🧪 ATTACK SIMULATOR
# --------------------------------------------------
st.subheader("🧪 Attack Simulation Console")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔓 Brute Force Attack"):
        result = listener.handle_event("auth_failed")
        st.error(result)

with col2:
    if st.button("🧠 Anomaly Detected"):
        result = listener.handle_event("anomaly_detected")
        st.warning(result)

with col3:
    if st.button("💥 Session Abuse"):
        result = listener.handle_event("session_abuse")
        st.error(result)

# --------------------------------------------------
# 🔁 FEEDBACK LOOP VIEW
# --------------------------------------------------
st.subheader("🔁 Trust Feedback Loop")

if trust_history:
    last = trust_history[-1]
    st.metric(
        label="Current Trust Score",
        value=last["trust"],
        delta=last["delta"]
    )
else:
    st.metric("Current Trust Score", "N/A")