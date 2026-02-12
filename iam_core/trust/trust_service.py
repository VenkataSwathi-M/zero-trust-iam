# iam_core/trust/trust_service.py

from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session

from iam_core.db.database import SessionLocal
from iam_core.db.models import TrustScore, TrustHistory  # MUST exist in models.py


# ----------------------------
# Helpers
# ----------------------------
def _get_or_create_trust_row(db: Session, agent_id: str) -> TrustScore:
    row = db.query(TrustScore).filter(TrustScore.subject == agent_id).first()
    if not row:
        row = TrustScore(subject=agent_id, score=50.0, updated_at=datetime.utcnow())
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


# ----------------------------
# REQUIRED EXPORT: update_trust
# ----------------------------
def update_trust(agent_id: str, delta: float, reason: str = "event") -> float:
    """
    Update trust score in DB (0..100) and write trust history.
    Returns new score.
    """
    db = SessionLocal()
    try:
        row = _get_or_create_trust_row(db, agent_id)
        new_score = max(0.0, min(100.0, float(row.score) + float(delta)))

        row.score = new_score
        row.updated_at = datetime.utcnow()

        hist = TrustHistory(
            agent_id=agent_id,
            score=new_score,
            reason=reason,
            created_at=datetime.utcnow(),
        )
        db.add(hist)
        db.commit()
        return new_score
    finally:
        db.close()


def get_trust(agent_id: str) -> float:
    """Read current trust score (0..100)."""
    db = SessionLocal()
    try:
        row = db.query(TrustScore).filter(TrustScore.subject == agent_id).first()
        return float(row.score) if row else 50.0
    finally:
        db.close()


def get_trust_metrics(limit: int = 50) -> dict:
    """
    For Admin Dashboard.
    Returns latest trust scores and recent trust history.
    """
    db = SessionLocal()
    try:
        scores = db.query(TrustScore).all()
        history = (
            db.query(TrustHistory)
            .order_by(TrustHistory.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "scores": [
                {"agent_id": s.subject, "score": float(s.score), "updated_at": s.updated_at}
                for s in scores
            ],
            "history": [
                {
                    "agent_id": h.agent_id,
                    "score": float(h.score),
                    "reason": h.reason,
                    "created_at": h.created_at,
                }
                for h in history
            ],
        }
    finally:
        db.close()

# ----------------------------
# Backward/compatibility API
# ----------------------------
# ----------------------------
# Backward/compatibility API
# ----------------------------
def apply_trust_event(
    db: Session,
    agent_id: str,
    event: str,
    delta: float | None = None,
    reason: str | None = None,
) -> float:
    """
    New + backward compatible.
    - Uses the SAME db session (so it works inside API routes)
    - Updates trust_scores (0..100)
    - Inserts trust_history
    - Syncs agents.trust_level (0..1)
    - Returns new trust score (0..100)
    """

    event = (event or "EVENT").upper()
    reason = reason or event

    # Default mapping if delta not provided
    mapping = {
        "AUTH_FAIL": -5,
        "OTP_FAIL": -5,
        "LOGIN_SUCCESS": +1,
        "OTP_OK": +1,
        "ACCESS_DENY": -3,
        "ACCESS_ALLOW": +0.5,
        "ANOMALY_DETECTED": -8,
        "SESSION_ABUSE": -6,
    }

    if delta is None:
        delta = mapping.get(event, 0)

    # --- trust_scores row ---
    row = db.query(TrustScore).filter(TrustScore.subject == agent_id).first()
    if not row:
        row = TrustScore(subject=agent_id, score=50.0, updated_at=datetime.utcnow())
        db.add(row)
        db.flush()  # don't commit here; caller controls transaction

    new_score = max(0.0, min(100.0, float(row.score) + float(delta)))
    row.score = new_score
    row.updated_at = datetime.utcnow()

    # --- trust_history insert ---
    hist = TrustHistory(
        agent_id=agent_id,
        score=new_score,
        reason=reason,
        created_at=datetime.utcnow(),
    )
    db.add(hist)

    # --- sync Agent table trust_level (0..1) ---
    from iam_core.db.models import Agent
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if agent:
        agent.trust_level = round(new_score / 100.0, 3)

    # caller will commit
    return new_score