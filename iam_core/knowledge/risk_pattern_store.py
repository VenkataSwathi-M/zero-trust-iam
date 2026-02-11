# iam_core/knowledge/risk_pattern_store.py
from datetime import datetime
from collections import defaultdict


class RiskPatternStore:
    """
    Stores historical risk patterns for learning & correlation
    """

    def __init__(self):
        # identity_id -> list of risk records
        self.history = defaultdict(list)

    def store(self, identity_id, event, risk_score, risk_level):
        record = {
            "event": event,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow()
        }
        self.history[identity_id].append(record)

    def get_recent_risks(self, identity_id, window=5):
        return self.history.get(identity_id, [])[-window:]

    def high_risk_frequency(self, identity_id):
        records = self.history.get(identity_id, [])
        return sum(1 for r in records if r["risk_level"] == "HIGH")


# -------------------------------
# Singleton Store
# -------------------------------

_STORE = RiskPatternStore()


def get_store() -> RiskPatternStore:
    return _STORE


def record_risk(identity_id: str, event: str, risk_score: float, risk_level: str):
    _STORE.store(identity_id, event, risk_score, risk_level)


# -------------------------------
# Adaptive Pattern Function
# -------------------------------

def get_patterns(identity_id: str | None = None) -> dict:
    """
    Returns adaptive multipliers per signal.
    RiskAssessmentEngine expects:
      {"anomaly": 1.2, "session_abuse": 1.1, ...}
    """

    patterns = {
        "auth_fail": 1.0,
        "deny": 1.0,
        "trust_decay": 1.0,
        "anomaly": 1.0,
        "session_abuse": 1.0,
    }

    if not identity_id:
        return patterns

    high_count = _STORE.high_risk_frequency(identity_id)

    # Adaptive learning rule
    if high_count >= 3:
        patterns["anomaly"] = 1.3
        patterns["session_abuse"] = 1.2
        patterns["deny"] = 1.1

    return patterns