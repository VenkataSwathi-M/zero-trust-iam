from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.db.models import AuditLog
from iam_core.auth.admin_deps import get_current_admin as require_admin

router = APIRouter(prefix="/admin/audit", tags=["Admin Audit"])

@router.get("/logs")
def get_logs(
    limit: int = 50,
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),   # ✅ THIS LINE PROTECTS IT
):
    q = db.query(AuditLog)
    if agent_id:
        q = q.filter(AuditLog.agent_id == agent_id)

    rows = q.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "event_type": r.event_type,
            "message": r.message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]