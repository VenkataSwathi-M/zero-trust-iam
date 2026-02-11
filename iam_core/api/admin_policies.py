from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from iam_core.db.database import get_db
from iam_core.db.models import Policy

router = APIRouter(prefix="/admin", tags=["Admin Policies"])

@router.post("/policies")
def create_policy(payload: dict, db: Session = Depends(get_db)):
    agent_id = payload.get("agent_id", "ALL")
    resource = payload.get("resource")
    action = payload.get("action")
    effect = payload.get("effect")  # ALLOW/DENY/STEP_UP
    min_trust = float(payload.get("min_trust", 0.0))

    if not resource or not action or effect not in ["ALLOW", "DENY", "STEP_UP"]:
        raise HTTPException(400, "resource, action, effect required")

    p = Policy(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        resource=resource,
        action=action,
        effect=effect,
        min_trust=min_trust
    )
    db.add(p)
    db.commit()
    return {"message": "Policy created"}