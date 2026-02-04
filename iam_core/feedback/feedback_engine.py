# iam_core/feedback/feedback_engine.py

from iam_core.trust.trust_store import update_trust
from iam_core.risk.risk_pattern_store import record_pattern


class FeedbackEngine:
    """
    Learns from decisions and updates trust & risk history
    """

    def apply(self, identity_id, decision, risk_score):
        # ---- Trust Adjustment Rules ----
        if decision == "DENY":
            delta = -10
        elif decision == "STEP_UP":
            delta = -5
        else:  # ALLOW
            delta = +2

        update_trust(identity_id, delta)

        # ---- Persist Risk Pattern ----
        record_pattern(
            identity_id=identity_id,
            risk_score=risk_score,
            decision=decision
        )

        return {
            "trust_delta": delta,
            "decision": decision
        }