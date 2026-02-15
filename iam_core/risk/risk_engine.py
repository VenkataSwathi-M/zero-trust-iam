# iam_core/risk/risk_engine.py
from dataclasses import dataclass

@dataclass
class RiskInput:
    auth_fail_rate: float = 0.0
    mfa_fail_rate: float = 0.0
    new_device: float = 0.0
    token_reuse_anomaly: float = 0.0
    request_spike: float = 0.0
    unusual_endpoint: float = 0.0
    high_priv_action: float = 0.0
    night_access: float = 0.0
    amount_anomaly: float = 0.0
    new_beneficiary: float = 0.0


def clamp01(x: float) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0


def risk_score_from_trust(trust: float) -> float:
    t = clamp01(trust)
    return round(1.0 - t, 2)


def risk_level(score: float) -> str:
    r = clamp01(score)
    if r >= 0.70:
        return "HIGH"
    if r >= 0.35:
        return "MEDIUM"
    return "LOW"


def compute_risk(inp: RiskInput) -> float:
    weights = {
        "auth_fail_rate": 0.15,
        "mfa_fail_rate": 0.10,
        "new_device": 0.10,
        "token_reuse_anomaly": 0.20,
        "request_spike": 0.10,
        "unusual_endpoint": 0.10,
        "high_priv_action": 0.10,
        "night_access": 0.05,
        "amount_anomaly": 0.05,
        "new_beneficiary": 0.05,
    }

    score = 0.0
    for k, w in weights.items():
        score += w * clamp01(getattr(inp, k, 0.0))
    return clamp01(score)


class RiskAssessmentEngine:
    def classify_risk(self, risk_score: float) -> str:
        return risk_level(risk_score)

    def assess(self, inp: RiskInput) -> tuple[float, str]:
        score = compute_risk(inp)
        return score, self.classify_risk(score)