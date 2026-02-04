class PolicyAgent:
    def evaluate(self, context):
        risk = context["risk_score"]
        anomaly = context["anomaly"]

        if anomaly:
            return "DENY"

        if risk >= 70:
            return "DENY"
        elif risk >= 40:
            return "RESTRICT"
        else:
            return "ALLOW"