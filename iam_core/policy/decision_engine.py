class DecisionEngine:
    """
    Resolves the final policy decision based on matched rules.

    Decision priority (Zero Trust):
    1. DENY
    2. STEP_UP
    3. ALLOW
    4. Default → DENY
    """

    def derive(self, matched_rules):
        if not matched_rules:
            return "DENY"

        effects = {rule["effect"] for rule in matched_rules if "effect" in rule}

        if "DENY" in effects:
            return "DENY"

        if "STEP_UP_AUTH" in effects or "STEP_UP" in effects:
            return "STEP_UP"

        if "ALLOW" in effects:
            return "ALLOW"

        return "DENY"