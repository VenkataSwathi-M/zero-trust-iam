# iam_core/trust/trust_service.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from iam_core.db.models import TrustScore, TrustHistory, Agent


# ------------------------------
# 1) Trust update (0.0 - 1.0 scale)
# ------------------------------
def update_trust(
    db: Session,
    agent_id: str,
    delta: float,
    reason: str = "event",
) -> float:
    """
    Updates Agent.trust_level (0.0 - 1.0) and inserts TrustHistory point.
    This is the function your EnforcementDispatcher expects.

    delta: +/- value in 0..1 scale (example: -0.10, +0.02)
    """
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return 0.0

    cur = float(agent.trust_level or 0.0)
    new_val = max(0.0, min(1.0, cur + float(delta)))
    agent.trust_level = round(new_val, 3)

    # store in trust_history (score field stores 0..1 in your project)
    db.add(
        TrustHistory(
            agent_id=agent_id,
            score=new_val,
            reason=reason,
        )
    )
    db.flush()
    return float(agent.trust_level)


# ------------------------------
# 2) Event-based trust (0 - 100 scale)
# (Optional if you want scoring in 0..100 too)
# ------------------------------
def apply_trust_event(
    db: Session,
    agent_id: str,
    event: str,
    delta: Optional[float] = None,
    reason: Optional[str] = None,
) -> float:
    """
    Event-based trust scoring (0..100). Also syncs Agent.trust_level (0..1).
    You can use this for 'signals'.
    """
    event = (event or "EVENT").upper()
    reason = reason or event

    mapping = {
        "AUTH_FAIL": -5,
        "OTP_FAIL": -5,
        "LOGIN_SUCCESS": +2,
        "OTP_OK": +2,
        "ACCESS_DENY": -3,
        "ACCESS_ALLOW": +1,
        "ANOMALY_DETECTED": -8,
        "SESSION_ABUSE": -6,
        "HIGH_RISK_TRANSFER": -10,
    }

    if delta is None:
        delta = mapping.get(event, 0)

    row = db.query(TrustScore).filter(TrustScore.subject == agent_id).first()
    if not row:
        row = TrustScore(subject=agent_id, score=50.0)
        db.add(row)
        db.flush()

    new_score = max(0.0, min(100.0, float(row.score) + float(delta)))
    row.score = new_score
    row.updated_at = datetime.utcnow()

    # Store history: here score is 0..100
    db.add(
        TrustHistory(
            agent_id=agent_id,
            score=new_score,
            reason=reason,
        )
    )

    # sync agent.trust_level 0..1
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if agent:
        agent.trust_level = round(new_score / 100.0, 3)

    db.flush()
    return float(new_score)


# ------------------------------
# 3) Required by dashboard.py
# ------------------------------
def get_trust_metrics(db: Session, agent_id: str, limit: int = 60):
    """
    Dashboard expects this function.
    Returns trust history points for chart (oldest -> newest).
    """
    rows = (
        db.query(TrustHistory)
        .filter(TrustHistory.agent_id == agent_id)
        .order_by(desc(TrustHistory.created_at))
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))  # oldest -> newest

    out = []
    for r in rows:
        t = r.created_at.isoformat() if r.created_at else None
        out.append(
            {
                "t": t,
                "trust": float(r.score),
                "reason": r.reason,
            }
        )
    return out