# iam_core/api/session_status.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from iam_core.auth.deps import get_current_identity
from iam_core.db.database import get_db
from iam_core.db.models import Agent
from iam_core.session.session_store import get_effective_trust, get_session

router = APIRouter(prefix="/session", tags=["Session"])

@router.get("/me")
def session_me(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    sid = identity["sid"]
    agent_id = identity["sub"]

    s = get_session(sid)
    eff = get_effective_trust(sid)

    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    max_access = (agent.max_access if agent else "read")

    return {
        "agent_id": agent_id,
        "sid": sid,
        "effective_trust": eff,
        "step_up": bool(s.get("step_up")) if s else False,
        "max_access": max_access,
    }