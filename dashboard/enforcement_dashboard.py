import sys
from pathlib import Path
import streamlit as st
from iam_core.enforcement.enforcement_dispatcher import ENFORCEMENT_LOG

st.set_page_config(page_title="Zero Trust Enforcement Dashboard", layout="wide")

st.title("🔐 Zero Trust Enforcement Dashboard")

if not ENFORCEMENT_LOG:
    st.info("No enforcement actions yet.")
else:
    for idx, record in enumerate(reversed(ENFORCEMENT_LOG)):
        with st.expander(f"Decision #{len(ENFORCEMENT_LOG)-idx}"):
            st.json(record)

            context = record.get("context", {})
            reason = context.get("authz_reason")

            if reason:
                st.error(f" Authorization Denied: {reason}")
            else:
                st.success(" Authorization Successful")
# ---- PYTHONPATH FIX ----
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
from iam_core.enforcement.enforcement_dispatcher import ENFORCEMENT_LOG

# ---- UI ----
st.set_page_config(page_title="Zero Trust Enforcement Dashboard", layout="wide")

st.title("🛡️ Zero Trust Enforcement Dashboard")
st.caption("Live Policy Enforcement & Feedback Loop")

# ---- Metrics ----
col1, col2, col3 = st.columns(3)

total_events = len(ENFORCEMENT_LOG)
deny_count = len([e for e in ENFORCEMENT_LOG if e["decision"] == "DENY"])
stepup_count = len([e for e in ENFORCEMENT_LOG if e["decision"] == "STEP_UP"])

col1.metric("Total Enforcement Events", total_events)
col2.metric("Denied Access", deny_count)
col3.metric("Step-Up Auth", stepup_count)

st.divider()

# ---- Enforcement Table ----
if ENFORCEMENT_LOG:
    df = pd.DataFrame(ENFORCEMENT_LOG)
    st.subheader("📜 Enforcement Decisions Log")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No enforcement events yet. Trigger access requests.")

# ---- Auto Refresh ----
st.caption("🔄 Refresh the page to see new enforcement actions")