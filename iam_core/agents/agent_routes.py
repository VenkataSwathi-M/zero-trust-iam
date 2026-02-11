from fastapi import APIRouter, HTTPException
from iam_core.db.models import Agent
from iam_core.db.database import get_db
from iam_core.auth.jwt_utils import create_access_token

agent_router = APIRouter(prefix="/agent", tags=["Agent"])

@agent_router.post("/login")
def agent_login(data: dict, db=Depends(get_db)):
    agent = db.query(Agent).filter(
        Agent.agent_id == data["agent_id"]
    ).first()

    if not agent:
        raise HTTPException(status_code=401, detail="Invalid agent")

    token = create_access_token({
        "sub": agent.agent_id,
        "role": "agent"
    })

    return {"access_token": token}