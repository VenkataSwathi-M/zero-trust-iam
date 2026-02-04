# iam_core/admin/admin_routes.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from iam_core.auth.jwt_utils import decode_access_token
from iam_core.session.session_store import get_session
from iam_core.metrics.store import METRICS
from iam_core.db.database import get_db
from iam_core.db.models import Agent

# ---------------- Security ----------------
security = HTTPBearer()

def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    session = get_session(payload["sid"])
    if not session or not session["active"]:
        raise HTTPException(status_code=401, detail="Session revoked")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return payload

# ---------------- Router ----------------
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# ---------------- Schemas ----------------
class AgentCreateRequest(BaseModel):
    max_access: str
    trust_level: float = 0.5

# ---------------- Metrics API ----------------
@admin_router.get("/metrics")
def get_metrics(identity=Depends(get_current_identity)):
    return {
        "transactions": METRICS["transactions"],
        "deny_rate": round(
            METRICS["denied"] / max(1, METRICS["transactions"]), 3
        ),
        "average_trust": round(
            sum(METRICS["trust_scores"]) /
            max(1, len(METRICS["trust_scores"])), 2
        ),
        "high_risk_events": METRICS["high_risk"],
        "policy_denials": METRICS["policy_denials"]
    }

# ---------------- Create Agent ----------------
@admin_router.post("/agents")
def create_agent(
    data: AgentCreateRequest,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"

    agent = Agent(
        agent_id=agent_id,
        max_access=data.max_access,
        trust_level=data.trust_level,
        created_by=identity["sub"]
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "message": "Agent created successfully",
        "agent": {
            "agent_id": agent.agent_id,
            "max_access": agent.max_access,
            "trust_level": agent.trust_level
        }
    }

# ---------------- List Agents ----------------
@admin_router.get("/agents")
def list_agents(
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    return db.query(Agent).all()