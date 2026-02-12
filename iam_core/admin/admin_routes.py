# iam_core/admin/admin_routes.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uuid

from iam_core.auth.jwt_utils import decode_access_token
from iam_core.session.session_store import get_session
from iam_core.metrics.store import METRICS
from iam_core.db.database import get_db
from iam_core.db.models import Agent, Policy  # ✅ add Policy
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from iam_core.auth.jwt_utils import decode_access_token
# ---------------- Security ----------------
security = HTTPBearer()

security = HTTPBearer()

def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ✅ Check role
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # ✅ Check session (THIS is where your sid logic goes)
    sid = payload.get("sid")
    if not sid:
        raise HTTPException(status_code=401, detail="Missing session id")

    session = get_session(sid)
    if not session or not session.get("active"):
        raise HTTPException(status_code=401, detail="Session revoked")

    return payload

# ---------------- Router ----------------
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# ---------------- Schemas ----------------
class AgentCreateRequest(BaseModel):
    max_access: str
    trust_level: float = 0.5

class PolicyCreateRequest(BaseModel):
    # policy scope (agent-specific or global)
    agent_id: str = Field(..., description='Use "ALL" for global policy')

    resource: str
    action: str

    effect: str = Field("ALLOW", description='ALLOW | DENY | STEP_UP')

    # your “professional” controls
    min_trust: float = 0.4
    max_risk: str = "HIGH"          # LOW / MEDIUM / HIGH
    max_amount: float | None = None # used for transfers
    require_mfa: bool = False

class PolicyUpdateRequest(BaseModel):
    effect: str | None = None
    min_trust: float | None = None
    max_risk: str | None = None
    max_amount: float | None = None
    require_mfa: bool | None = None

# ---------------- Metrics API ----------------
@admin_router.get("/metrics")
def get_metrics(identity=Depends(get_current_identity)):
    return {
        "transactions": METRICS.get("transactions", 0),
        "deny_rate": round(
            METRICS.get("denied", 0) / max(1, METRICS.get("transactions", 0)), 3
        ),
        "average_trust": round(
            sum(METRICS.get("trust_scores", [])) / max(1, len(METRICS.get("trust_scores", []))), 2
        ),
        "high_risk_events": METRICS.get("high_risk", 0),
        "policy_denials": METRICS.get("policy_denials", 0),
    }

# ✅ Your frontend is calling /admin/metrics/overview → add it
@admin_router.get("/metrics/overview")
def metrics_overview(
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db),
):
    total_agents = db.query(Agent).count()
    total_policies = db.query(Policy).count()

    # keep whatever you already show + counts
    return {
        "transactions": METRICS.get("transactions", 0),
        "denied": METRICS.get("denied", 0),
        "deny_rate": round(
            METRICS.get("denied", 0) / max(1, METRICS.get("transactions", 0)), 3
        ),
        "high_risk_events": METRICS.get("high_risk", 0),
        "policy_denials": METRICS.get("policy_denials", 0),
        "total_agents": total_agents,
        "total_policies": total_policies,
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

# ---------------- Policies ----------------
@admin_router.get("/policies")
def list_policies(
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    return db.query(Policy).all()

@admin_router.post("/policies")
def create_policy(
    data: PolicyCreateRequest,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    p = Policy(
        id=str(uuid.uuid4()),
        agent_id=data.agent_id,
        resource=data.resource,
        action=data.action,
        effect=data.effect,
        min_trust=data.min_trust,
        max_risk=data.max_risk,
        max_amount=data.max_amount,
        require_mfa=data.require_mfa,
        created_by=identity["sub"],
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"message": "Policy created", "policy": p}

@admin_router.put("/policies/{policy_id}")
def update_policy(
    policy_id: str,
    data: PolicyUpdateRequest,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    p = db.query(Policy).filter(Policy.id == policy_id).first()
    if not p:
        raise HTTPException(404, "Policy not found")

    if data.effect is not None: p.effect = data.effect
    if data.min_trust is not None: p.min_trust = data.min_trust
    if data.max_risk is not None: p.max_risk = data.max_risk
    if data.max_amount is not None: p.max_amount = data.max_amount
    if data.require_mfa is not None: p.require_mfa = data.require_mfa

    db.commit()
    db.refresh(p)
    return {"message": "Policy updated", "policy": p}

@admin_router.delete("/policies/{policy_id}")
def delete_policy(
    policy_id: str,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    p = db.query(Policy).filter(Policy.id == policy_id).first()
    if not p:
        raise HTTPException(404, "Policy not found")
    db.delete(p)
    db.commit()
    return {"message": "Policy deleted"}