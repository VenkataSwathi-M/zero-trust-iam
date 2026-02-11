from datetime import datetime
from sqlalchemy.orm import Session

from iam_core.db.database import SessionLocal
from iam_core.db.models import TrustScore


class TrustHistoryStore:
    def record(self, identity_id: str, score: float, context: dict):
        db: Session = SessionLocal()
        try:
            # placeholder for audit logging / future table
            print(
                f"[TRUST HISTORY] {identity_id} → {score} | {context} @ {datetime.utcnow()}"
            )
        finally:
            db.close()