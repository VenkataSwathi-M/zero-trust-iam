class RiskAgent:
    def assess(self, identity, action, resource):
        risk = 0

        if action == "transfer_funds":
            risk += 30
        if resource.startswith("account"):
            risk += 20
        if not identity.get("mfa_enabled"):
            risk += 20

        return min(risk, 100)