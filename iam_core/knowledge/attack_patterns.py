ATTACK_PATTERNS = {
    "brute_force": {
        "signals": ["auth_fail", "session_abuse"],
        "base_risk": 0.6
    },
    "account_takeover": {
        "signals": ["anomaly", "trust_decay"],
        "base_risk": 0.7
    },
    "fraud_transaction": {
        "signals": ["anomaly", "deny"],
        "base_risk": 0.8
    }
}