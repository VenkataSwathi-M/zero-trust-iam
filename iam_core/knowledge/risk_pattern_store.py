from datetime import datetime
from collections import defaultdict

class RiskPatternStore:
    def __init__(self):
        self.history = defaultdict(list)

    def store(self, identity_id, event, risk_score, risk_level):
        self.history[identity_id].append({
            "event": event,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow()
        })

    def high_risk_frequency(self, identity_id):
        records = self.history.get(identity_id, [])
        return sum(1 for r in records if r["risk_level"] == "HIGH")


_STORE = RiskPatternStore()

def record_risk(identity_id: str, event: str, risk_score: float, risk_level: str):
    _STORE.store(identity_id, event, risk_score, risk_level)

def record_pattern(identity_id: str, pattern: str, risk_level: str):
    _STORE.store(identity_id, event=f"pattern:{pattern}", risk_score=0.0, risk_level=risk_level)

def get_patterns(identity_id: str | None = None) -> dict:
    if not identity_id:
        return {}

    high_count = _STORE.high_risk_frequency(identity_id)

    patterns = {
        "auth_fail": 1.0,
        "deny": 1.0,
        "trust_decay": 1.0,
        "anomaly": 1.0,
        "session_abuse": 1.0,
    }

    if high_count >= 3:
        patterns["anomaly"] = 1.3
        patterns["session_abuse"] = 1.2
        patterns["deny"] = 1.1

    return patterns