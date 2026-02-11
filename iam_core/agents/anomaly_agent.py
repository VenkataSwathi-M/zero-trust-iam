def should_block(pattern: str, risk_level: str, trust: float):
    # hard block
    if trust < 0.2:
        return True, "trust_too_low"

    # repeated high-risk pattern => block
    if pattern in ["DESTRUCTIVE_ACTION"] and risk_level in ["HIGH", "MEDIUM"]:
        return True, "destructive_action"

    return False, "ok"