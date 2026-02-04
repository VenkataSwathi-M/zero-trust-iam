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