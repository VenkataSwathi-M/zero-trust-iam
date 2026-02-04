from iam_core.trust.trust_history_store import record_trust, get_trust_history
from iam_core.knowledge.risk_pattern_store import update_pattern, get_patterns

class RiskAssessmentEngine:

    def assess(self, identity_id, signals, trust_score, risk_level):
        """
        Core reasoning engine
        """

        # ---- Store trust history ----
        record_trust(identity_id, trust_score, risk_level)

        history = get_trust_history(identity_id)
        patterns = get_patterns()

        # ---- Pattern Detection Logic ----
        if signals.get("auth_fail", 0) > 0:
            update_pattern("auth_fail_spike")

        if signals.get("anomaly", 0) > 0:
            update_pattern("anomaly_cluster")

        if trust_score < 40 and len(history) > 3:
            update_pattern("trust_decay_loop")

        return {
            "risk_level": risk_level,
            "trust_score": trust_score,
            "history_depth": len(history),
            "active_patterns": patterns
        }