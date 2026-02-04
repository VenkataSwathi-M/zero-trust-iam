# iam_core/risk/risk_engine.py

class RiskAssessmentEngine:
    """
    Computes dynamic risk score with adaptive weights
    """

    def __init__(self):
        self.base_weights = {
            "auth_fail": 0.25,
            "deny": 0.20,
            "trust_decay": 0.20,
            "anomaly": 0.25,
            "session_abuse": 0.10
        }

    def adapt_weights(self, high_risk_count):
        """
        Increase sensitivity for repeated high-risk behavior
        """
        weights = self.base_weights.copy()

        if high_risk_count >= 3:
            weights["anomaly"] += 0.10
            weights["session_abuse"] += 0.05

        return weights

    def calculate_risk(self, signals, high_risk_count=0):
        weights = self.adapt_weights(high_risk_count)

        risk = sum(
            weights[key] * signals.get(key, 0)
            for key in weights
        )

        return round(min(max(risk, 0), 1), 2)

    def classify_risk(self, risk_score):
        if risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"