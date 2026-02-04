from iam_core.risk.risk_engine import RiskAssessmentEngine
from iam_core.knowledge.security_knowledge_base import SecurityKnowledgeBase
from iam_core.policy.policy_reasoner import PolicyReasoner


class SecurityEventListener:
    """
    Converts security events into risk signals
    """

    def __init__(self):
        self.risk_engine = RiskAssessmentEngine()
        self.knowledge_base = SecurityKnowledgeBase()
        self.policy_reasoner = PolicyReasoner()

    def handle_event(self, event_type, metadata=None):
        metadata = metadata or {}

        event_profile = self.knowledge_base.get_event_profile(event_type)

        signals = {
            "auth_fail": 0,
            "deny": 0,
            "trust_decay": event_profile["trust_decay"],
            "anomaly": 0,
            "session_abuse": 0
        }

        if event_type == "auth_failed":
            signals["auth_fail"] = 1
        elif event_type == "access_denied":
            signals["deny"] = 1
        elif event_type == "anomaly_detected":
            signals["anomaly"] = 1
        elif event_type == "session_abuse":
            signals["session_abuse"] = 1

        risk_score = self.risk_engine.calculate_risk(signals)
        risk_level = self.risk_engine.classify_risk(risk_score)

        policy_decision = self.policy_reasoner.decide(
            signals=signals,
            risk_score=risk_score,
            risk_level=risk_level,
            metadata=metadata
        )

        return {
            "event": event_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "decision": policy_decision["decision"],
            "matched_rules": policy_decision["matched_rules"]
        }