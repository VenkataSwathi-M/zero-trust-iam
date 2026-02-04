import streamlit as st
import time
import sys
from pathlib import Path

# Add parent directory to path so we can import iam_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from iam_core.trust.trust_store import (
    get_current_trust,
    get_trust_history
)

st.set_page_config(layout="wide")
st.title("🛡️ Zero Trust – Live Trust Monitor")

identity_id = st.selectbox(
    "Select Identity",
    ["user1", "user2", "agentA"]
)

placeholder = st.empty()

while True:
    with placeholder.container():
        current = get_current_trust(identity_id)
        history = get_trust_history(identity_id)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Current Trust Score",
                current,
                delta=history[-1]["delta"] if history else 0
            )

        with col2:
            st.write("Trust Level:")
            if current >= 80:
                st.success("HIGH")
            elif current >= 50:
                st.warning("MEDIUM")
            else:
                st.error("LOW")

        if history:
            st.subheader("Trust History")
            st.line_chart([h["trust"] for h in history])

    time.sleep(2)