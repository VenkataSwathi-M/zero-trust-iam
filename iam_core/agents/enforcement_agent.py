class EnforcementAgent:
    def enforce(self, context):
        decision = context["policy_decision"]

        if decision == "DENY":
            return {"decision": "DENY", "reason": "High Risk"}
        elif decision == "RESTRICT":
            return {"decision": "RESTRICT", "limits": "Read-only"}
        else:
            return {"decision": "ALLOW"}