from iam_core.policy.context_builder import ContextBuilder
from iam_core.policy.rule_evaluator import RuleEvaluator
from iam_core.policy.decision_engine import DecisionEngine
from iam_core.trust.decay import apply_trust_decay

class PolicyReasoner:
    """
    Zero Trust Policy Decision Point (PDP)
    RBAC → PBAC → ABAC → Trust → Enforcement
    """

    def __init__(self):
        self.context_builder = ContextBuilder()
        self.rule_evaluator = RuleEvaluator()
        self.decision_engine = DecisionEngine()

    def decide(self, signals, risk_score, risk_level, metadata=None):

        # 1️⃣ Build context
        context = self.context_builder.build_context(
            signals=signals,
            risk_score=risk_score,
            risk_level=risk_level,
            metadata=metadata
        )

        # 2️⃣ PBAC rule evaluation
        matched_rules = self.rule_evaluator.evaluate(context)

        # 3️⃣ Decision derivation
        decision = self.decision_engine.derive(matched_rules)

        # 4️⃣ Trust decay (Zero Trust principle)
        apply_trust_decay(
            identity_id=context.get("subject"),
            minutes_idle=context.get("idle_minutes", 0)
        )

        # 5️⃣ Return explainable decision
        return {
            "decision": decision,
            "matched_rules": [r["id"] for r in matched_rules],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "context": context
        }