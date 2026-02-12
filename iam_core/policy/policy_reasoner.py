from iam_core.db.models import Policy

class PolicyReasoner:
    def decide(self, db, agent_id: str, trust: float, resource: str, action: str, pattern: str):
        # 1) exact agent policy
        p = db.query(Policy).filter(
            Policy.agent_id == agent_id,
            Policy.resource == resource,
            Policy.action == action
        ).first()

        # 2) fallback global policy
        if not p:
            p = db.query(Policy).filter(
                Policy.agent_id == "ALL",
                Policy.resource == resource,
                Policy.action == action
            ).first()

        # 3) if policy exists, enforce min_trust + effect
        if p:
            if trust < p.min_trust:
                return {"decision": "DENY", "reason": "min_trust_not_met", "policy": p.effect}
            return {"decision": p.effect, "reason": "policy_match"}

        # 4) default zero-trust logic
        if pattern in ["TRANSFER_ATTEMPT", "DESTRUCTIVE_ACTION"]:
            return {"decision": "STEP_UP", "reason": "high_risk_pattern"}

        if trust < 0.4:
            return {"decision": "DENY", "reason": "low_trust"}

        return {"decision": "ALLOW", "reason": "default_allow"}
    
    RISK_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}

    def risk_ok(current: str, max_allowed: str) -> bool:
        return self.RISK_ORDER.get(current, 3) <= self.RISK_ORDER.get(max_allowed, 3)