from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from iam_core.db.database import get_db
from iam_core.db.models import Agent
from iam_core.auth.jwt_utils import create_access_token

router = APIRouter(prefix="/agent", tags=["Agent Auth"])

@router.post("/login")
def agent_login(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(
        Agent.agent_id == agent_id,
        Agent.active == True
    ).first()

    if not agent:
        raise HTTPException(status_code=401, detail="Invalid agent")

    token = create_access_token({
        "sub": agent.agent_id,
        "role": "agent"
    })

    return {"access_token": token}