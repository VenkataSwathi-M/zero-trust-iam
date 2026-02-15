from iam_core.risk.adaptive_risk_engine import AdaptiveRiskEngine
from iam_core.trust.trust_store import update_trust
from iam_core.risk.risk_pattern_store import RiskPatternStore

class TrustFeedbackProcessor:

    def __init__(self):
        self.pattern_store = RiskPatternStore()
        self.risk_engine = AdaptiveRiskEngine()

    def process(self, identity_id, decision, risk_score, signals):

        # ---- Trust Update ----
        if decision == "ALLOW":
            trust_delta = +2
        elif decision == "STEP_UP_AUTH":
            trust_delta = -5
        else:
            trust_delta = -15

        update_trust(identity_id, trust_delta)

        # ---- Learn Risk Pattern ----
        self.pattern_store.record_pattern(
            identity_id=identity_id,
            risk_score=risk_score,
            signals=signals,
            outcome=decision
        )

        # ---- ADAPT WEIGHTS ----
        self.risk_engine.adapt_weights(signals, decision)

        return {
            "trust_delta": trust_delta,
            "updated_weights": self.risk_engine.weights
        }