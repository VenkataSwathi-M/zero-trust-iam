import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.auth.deps import get_current_identity
from iam_core.db.models import AuditLog
from iam_core.security.access_guard import require_access
from iam_core.session.session_store import bump_trust

router = APIRouter(prefix="/banking/write", tags=["Banking-Write"])

@router.post("/profile")
def update_profile(req: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    require_access(db, identity, required="write", reason="Updating profile", trust_min=0.55)

    # simulate write success
    bump_trust(identity["sid"], +0.02)

    db.add(AuditLog(
        id=str(uuid.uuid4()),
        agent_id=identity["sub"],
        event_type="PROFILE_UPDATE",
        message=f"Profile updated name={req.get('name')} phone={req.get('phone')}"
    ))
    db.commit()

    return {"ok": True, "message": "Profile updated"}