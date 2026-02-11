from sqlalchemy.orm import Session
from iam_core.db.database import SessionLocal
from iam_core.db.models import TrustScore


class TrustStore:
    def __init__(self):
        self._cache = {}

    def get_trust(self, subject: str) -> float:
        if subject in self._cache:
            return self._cache[subject]

        db: Session = SessionLocal()
        record = db.query(TrustScore).filter_by(subject=subject).first()
        db.close()

        score = record.score if record else 50.0
        self._cache[subject] = score
        return score

    def update_trust(self, subject: str, delta: float):
        db: Session = SessionLocal()
        record = db.query(TrustScore).filter_by(subject=subject).first()

        if not record:
            record = TrustScore(subject=subject, score=50.0)
            db.add(record)

        record.score = max(0, min(100, record.score + delta))
        db.commit()
        db.close()

        self._cache[subject] = record.score

    # ---- Singleton Trust Store ----
_trust_store = TrustStore()


def get_current_trust(identity_id: str):
    """
    Returns current trust score for an identity
    """
    return _trust_store.get_trust(identity_id)


def get_trust_history(identity_id: str):
    """
    Returns trust history for an identity
    """
    return _trust_store.get_history(identity_id)