from iam_core.trust.trust_store import update_trust

class TrustFeedbackProcessor:
    """
    Feedback loop that updates trust based on enforcement decisions
    """

    def process(self, identity_id, decision, risk_score, signals):
        delta = 0

        if decision == "ALLOW":
            delta += 1
        elif decision == "STEP_UP":
            delta -= 2
        elif decision == "DENY":
            delta -= 5

        if signals.get("anomaly"):
            delta -= 3

        update_trust(identity_id, delta)

        return {
            "identity": identity_id,
            "trust_delta": delta,
            "risk_score": risk_score
        }