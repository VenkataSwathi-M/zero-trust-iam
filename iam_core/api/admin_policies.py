# iam_core/api/admin_policies.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
from iam_core.db.database import get_db
from iam_core.db.models import Policy, AuditLog
from iam_core.auth.admin_deps import get_current_admin # ✅ admin auth

router = APIRouter(prefix="/admin", tags=["Admin Policies"])

EFFECTS = {"ALLOW", "DENY", "STEP_UP"}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}


class PolicyCreate(BaseModel):
    name: str
    agent_id: str = "ALL"
    resource: str
    action: str
    effect: str = "ALLOW"
    min_trust: float = 0.0
    max_risk: str = "HIGH"
    max_amount: float | None = None
    require_mfa: bool = False
    active: bool = True
    priority: int = 1


@router.post("/policies")
def create_policy(
    data: PolicyCreate,
    identity=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    # validations
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Policy name is required")
    if not data.resource.strip():
        raise HTTPException(status_code=400, detail="resource is required")
    if not data.action.strip():
        raise HTTPException(status_code=400, detail="action is required")

    if data.effect not in EFFECTS:
        raise HTTPException(status_code=400, detail="Invalid effect")
    if data.max_risk not in RISK_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid max_risk")
    if data.min_trust < 0 or data.min_trust > 1:
        raise HTTPException(status_code=400, detail="min_trust must be 0.0 - 1.0")

    p = Policy(
        id=str(uuid.uuid4()),
        name=data.name.strip(),
        agent_id=(data.agent_id or "ALL").strip(),
        resource=data.resource.strip(),
        action=data.action.strip(),
        effect=data.effect,
        min_trust=float(data.min_trust),
        max_risk=data.max_risk,
        max_amount=data.max_amount,
        require_mfa=bool(data.require_mfa),
        active=bool(data.active),
        priority=int(data.priority),
    )

    db.add(p)

    # ✅ audit log
    db.add(
        AuditLog(
            id=str(uuid.uuid4()),
            agent_id=str(identity.get("sub", "ADMIN")),
            event_type="POLICY_CREATED",
            message=f"Policy '{p.name}' created for agent_id={p.agent_id} {p.resource}:{p.action} effect={p.effect}",
        )
    )

    db.commit()
    db.refresh(p)

    return {"message": "Policy created", "policy": p}


@router.get("/policies")
def list_policies(
    identity=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(Policy).order_by(Policy.created_at.desc()).all()





