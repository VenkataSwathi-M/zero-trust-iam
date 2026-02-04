class FeedbackLoop:

    def update_trust(self, trust, risk_level):
        if risk_level == "LOW":
            trust += 2
        elif risk_level == "HIGH":
            trust -= 5
        return max(0, min(trust, 100))

    def adjust_weights(self, weights, risk_level):
        if risk_level == "HIGH":
            weights["anomaly"] += 0.02
            weights["auth_fail"] += 0.01
        return weights