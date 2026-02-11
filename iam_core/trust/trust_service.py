# iam_core/trust/trust_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func

from iam_core.db.database import SessionLocal
from iam_core.db.models import TrustScore
from iam_core.db.models import Agent, TrustHistory

def update_trust(agent_id, delta, reason, db):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return

    old = agent.trust_level
    agent.trust_level = max(0, min(1, old + delta))

    history = TrustHistory(
        agent_id=agent_id,
        old_score=old,
        new_score=agent.trust_level,
        reason=reason
    )

    db.add(history)
    db.commit()

def get_trust_metrics():
    """
    Metrics for dashboard:
    - total identities
    - average trust score
    - low trust count
    """

    db: Session = SessionLocal()
    try:
        total_identities = db.query(TrustScore).count()

        avg_trust = (
            db.query(func.avg(TrustScore.score)).scalar() or 0.0
        )

        low_trust = (
            db.query(TrustScore)
            .filter(TrustScore.score < 40)
            .count()
        )

        return {
            "total_identities": total_identities,
            "average_trust": round(avg_trust, 2),
            "low_trust_identities": low_trust,
        }
    finally:
        db.close()