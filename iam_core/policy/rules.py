RULES = [
    # -------------------------------
    # High Risk → Immediate Deny
    # -------------------------------
    {
        "id": "R1_HIGH_RISK_DENY",
        "effect": "DENY",
        "condition": lambda ctx: ctx.get("risk_score", 0) > 0.7
    },

    # -------------------------------
    # Transfer with Low Trust → MFA
    # -------------------------------
    {
        "id": "R2_LOW_TRUST_TRANSFER_STEP_UP",
        "effect": "STEP_UP",
        "condition": lambda ctx: (
            ctx.get("action") == "transfer" and
            ctx.get("subject_attrs", {}).get("trust_level", 0) < 0.7
        )
    },

    # -------------------------------
    # Explicit High Risk Level → Deny
    # -------------------------------
    {
        "id": "R3_BLOCK_HIGH_RISK_LEVEL",
        "effect": "DENY",
        "condition": lambda ctx: ctx.get("risk_level") == "HIGH"
    },

    # -------------------------------
    # Medium Risk → Step-Up Auth
    # -------------------------------
    {
        "id": "R4_STEP_UP_MEDIUM_RISK",
        "effect": "STEP_UP",
        "condition": lambda ctx: ctx.get("risk_level") == "MEDIUM"
    },

    # -------------------------------
    # Anomaly Spike → Deny
    # -------------------------------
    {
        "id": "R5_BLOCK_ANOMALY_SPIKE",
        "effect": "DENY",
        "condition": lambda ctx: (
            ctx.get("signals", {}).get("anomaly", 0) == 1 and
            ctx.get("risk_score", 0) > 0.5
        )
    },

    # -------------------------------
    # Low Risk → Allow
    # -------------------------------
    {
        "id": "R6_ALLOW_LOW_RISK",
        "effect": "ALLOW",
        "condition": lambda ctx: ctx.get("risk_level") == "LOW"
    }
]