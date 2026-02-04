RULES = [
    {
        "id": "HIGH_RISK_DENY",
        "effect": "DENY",
        "condition": lambda ctx: ctx["risk_score"] > 0.7
    },
    {
        "id": "LOW_TRUST_TRANSFER",
        "effect": "STEP_UP",
        "condition": lambda ctx: (
            ctx["action"] == "transfer" and
            ctx["subject_attrs"]["trust_level"] < 0.7
        )
    }
]