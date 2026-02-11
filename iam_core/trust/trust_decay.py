# iam_core/trust/trust_decay.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from iam_core.db.database import SessionLocal
from iam_core.db.models import TrustScore


def apply_trust_decay(identity_id: str, minutes_idle: int):
    """
    Apply trust decay based on inactivity (Zero Trust principle).
    Reduces trust score gradually when the identity is idle.
    """

    if minutes_idle <= 0:
        return

    decay_rate = 0.1  # trust points per minute idle
    decay_amount = minutes_idle * decay_rate

    db: Session = SessionLocal()
    try:
        record = (
            db.query(TrustScore)
            .filter(TrustScore.identity_id == identity_id)
            .first()
        )

        if not record:
            return

        # Apply decay
        record.score = max(0, record.score - decay_amount)
        record.last_updated = datetime.utcnow()

        db.commit()

    finally:
        db.close()