# iam_core/risk/risk_pattern_store.py

from datetime import datetime

from blinker import signal

RISK_HISTORY = []


def store_risk_event(identity, signals, risk_score, risk_level):
    RISK_HISTORY.append({
        "identity": identity,
        "signals": signals,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "timestamp": datetime.utcnow().isoformat()
    })

class RiskPatternStore:
    """
    Stores historical risk patterns for learning & tuning
    """

    _patterns = []

    def record_pattern(self, identity_id, risk_score, signals, outcome):
        record = {
            "identity_id": identity_id,
            "risk_score": risk_score,
            "signals": signals,
            "outcome": outcome,
            "timestamp": datetime.utcnow()
        }
        self._patterns.append(record)

    def get_recent_patterns(self, limit=50):
        return self._patterns[-limit:]
    
    RISK_PATTERNS = {
        "auth_fail": 1,
        "deny": 1,
        "trust_decay": 1,
        "anomaly": 1,
        "session_abuse": 1
    }

    def update_pattern(self, signal, impact):
        self.RISK_PATTERNS[signal] += impact
        self.RISK_PATTERNS[signal] = max(0.5, min(2.0, self.RISK_PATTERNS[signal]))


    def get_patterns(self):
        return self.RISK_PATTERNS