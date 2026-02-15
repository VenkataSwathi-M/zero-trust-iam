from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.db.models import Agent
from iam_core.auth.deps import get_current_identity

router = APIRouter(prefix="/agent", tags=["Agent Profile"])

@router.get("/me")
def me(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(404, "Agent not found")

    return {
        "agent_id": agent.agent_id,
        "email": agent.email,
        "trust_level": float(agent.trust_level),
        "max_access": agent.max_access,
        "mfa_enabled": bool(agent.mfa_enabled),
        "active": bool(agent.active),
    }