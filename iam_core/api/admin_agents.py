from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from iam_core.db.database import get_db
from iam_core.db.models import Agent

router = APIRouter(prefix="/admin/agents", tags=["Admin Agents"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("")
def create_agent(payload: dict, db: Session = Depends(get_db)):
    if db.query(Agent).filter(Agent.agent_id == payload["agent_id"]).first():
        raise HTTPException(status_code=400, detail="Agent already exists")

    agent = Agent(
        agent_id=payload["agent_id"],
        email=payload["email"],
        hashed_password=hash_password(payload["password"]),
        max_access=payload.get("max_access", "read"),
        trust_level=payload.get("trust_level", 0.5),
        mfa_enabled=True
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "agent_id": agent.agent_id,
        "email": agent.email,
        "max_access": agent.max_access,
        "trust_level": agent.trust_level
    }

@router.get("")
def get_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()