# Stores trust evolution per identity

TRUST_HISTORY = {}

def record_trust(identity_id, trust_score, risk_level):
    TRUST_HISTORY.setdefault(identity_id, []).append({
        "trust": trust_score,
        "risk": risk_level
    })

def get_trust_history(identity_id):
    return TRUST_HISTORY.get(identity_id, [])