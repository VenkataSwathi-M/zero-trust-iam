# iam_core/enforcement/rule_generator.py

class EnforcementRuleGenerator:
    """
    Generates enforcement rules from policy decisions
    """

    def generate(self, decision, context):
        """
        decision: ALLOW / DENY / STEP_UP_AUTH
        context: full policy context
        """

        rules = []

        if decision == "DENY":
            rules.append({
                "action": "BLOCK",
                "reason": "High risk detected",
                "risk_level": context["risk_level"]
            })

        elif decision == "STEP_UP_AUTH":
            rules.append({
                "action": "REQUIRE_MFA",
                "reason": "Medium risk – step-up required",
                "risk_score": context["risk_score"]
            })

        elif decision == "ALLOW":
            rules.append({
                "action": "ALLOW",
                "constraints": {
                    "monitor": True,
                    "session_timeout": 300
                }
            })

        return rules