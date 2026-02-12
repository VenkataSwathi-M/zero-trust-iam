# iam_core/api/admin_policies.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from iam_core.db.database import get_db
from iam_core.db.models import Policy
from iam_core.admin.admin_routes import get_current_identity  # reuse your admin auth

router = APIRouter(prefix="/admin", tags=["Admin Policies"])

class PolicyCreate(BaseModel):
    name: str
    agent_id: str = "ALL"
    resource: str
    action: str
    effect: str = "ALLOW"   # ALLOW / DENY / STEP_UP
    min_trust: float = 0.0
    max_risk: str = "HIGH"  # LOW / MEDIUM / HIGH
    max_amount: float | None = None
    require_mfa: bool = False
    active: bool = True
    priority: int = 1

@router.post("/policies")
def create_policy(
    data: PolicyCreate,
    identity=Depends(get_current_identity),   # ✅ requires admin token
    db: Session = Depends(get_db)
):
    if data.effect not in ["ALLOW", "DENY", "STEP_UP"]:
        raise HTTPException(400, "Invalid effect")

    p = Policy(
        id=str(uuid.uuid4()),
        name=data.name.strip(),
        agent_id=data.agent_id.strip() if data.agent_id else "ALL",
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
    db.commit()
    db.refresh(p)

    return {"message": "Policy created", "policy": p}

@router.get("/policies")
def list_policies(
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    return db.query(Policy).all()