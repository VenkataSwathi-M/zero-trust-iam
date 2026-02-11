# iam_core/risk/risk_engine.py

from iam_core.knowledge.risk_pattern_store import get_patterns


def risk_score_from_trust(trust: float) -> float:
    """Simple risk score derived from trust."""
    return round(1 - float(trust), 2)


def risk_level(score: float) -> str:
    """Convert numeric risk into label."""
    if score >= 0.7:
        return "HIGH"
    if score >= 0.4:
        return "MEDIUM"
    return "LOW"


class RiskAssessmentEngine:
    """
    Computes dynamic risk score with adaptive multipliers.
    """

    def __init__(self):
        self.base_weights = {
            "auth_fail": 0.25,
            "deny": 0.20,
            "trust_decay": 0.20,
            "anomaly": 0.25,
            "session_abuse": 0.10,
        }

    def adapt_weights(self, high_risk_count: int):
        """
        Increase sensitivity for repeated high-risk behavior.
        """
        weights = self.base_weights.copy()

        if high_risk_count >= 3:
            weights["anomaly"] += 0.10
            weights["session_abuse"] += 0.05

        return weights

    def calculate_risk(self, signals: dict, identity_id: str | None = None) -> float:
        """
        signals example:
          {"anomaly":1, "deny":0, "auth_fail":0, "session_abuse":0, "trust_decay":0}

        get_patterns() returns adaptive multipliers per signal like:
          {"anomaly": 1.3, "deny": 1.1, ...}
        """
        patterns = get_patterns(identity_id)  # ✅ multipliers
        risk = 0.0

        for signal, value in signals.items():
            weight = self.base_weights.get(signal, 0.0)
            adaptive = patterns.get(signal, 1.0)
            risk += weight * adaptive * float(value)

        return round(min(risk, 1.0), 2)

    def classify_risk(self, risk_score: float) -> str:
        return risk_level(risk_score)