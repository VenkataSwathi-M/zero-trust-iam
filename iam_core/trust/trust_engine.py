from dataclasses import dataclass

@dataclass
class TrustResult:
    trust: float  # 0..1

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def update_trust(current_trust: float, risk_score: float, signals: dict) -> TrustResult:
    """
    signals:
    mfa_success, login_success, password_reset, new_device, ip_change, rate_spike
    """
    t = float(current_trust)

    # good signals (small boost)
    if signals.get("login_success"):
        t += 0.02
    if signals.get("mfa_success"):
        t += 0.05

    # penalties
    if signals.get("password_reset"):
        t -= 0.05
    if signals.get("new_device"):
        t -= 0.10
    if signals.get("rate_spike"):
        t -= 0.08

    # strongest penalty
    if signals.get("ip_change"):
        t -= 0.35

    # always penalize by risk score
    t -= 0.40 * risk_score

    return TrustResult(trust=clamp01(t))