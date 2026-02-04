from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import asyncio

from iam_core.db.database import get_db
from iam_core.db.models import Agent, AccessDecision
from iam_core.policy.policy_reasoner import PolicyReasoner
from iam_core.auth.deps import get_current_identity
from iam_core.api.ws import broadcast_decision

router = APIRouter(prefix="/api", tags=["Access"])
policy_engine = PolicyReasoner()


@router.post("/request-access")
def request_access(
    resource: str,
    action: str,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    """
    Agent → Request banking / DB resource
    """

    # -------------------------
    # Fetch agent
    # -------------------------
    agent = db.query(Agent).filter(
        Agent.agent_id == identity["sub"],
        Agent.active == True
    ).first()

    if not agent:
        raise HTTPException(status_code=403, detail="Agent not found or inactive")

    # -------------------------
    # Policy Decision
    # -------------------------
    risk_score = round(1 - agent.trust_level, 2)
    risk_level = (
        "HIGH" if agent.trust_level < 0.4
        else "MEDIUM" if agent.trust_level < 0.7
        else "LOW"
    )

    decision_result = policy_engine.decide(
        signals={
            "trust_level": agent.trust_level,
            "resource": resource,
            "action": action
        },
        risk_score=risk_score,
        risk_level=risk_level
    )

    decision = decision_result["decision"]  # ALLOW / DENY / STEP_UP

    # -------------------------
    # Store Decision (DB)
    # -------------------------
    record = AccessDecision(
        id=str(uuid.uuid4()),
        agent_id=agent.agent_id,
        resource=resource,
        action=action,
        decision=decision,
        risk_score=risk_score
    )

    db.add(record)
    db.commit()

    # -------------------------
    # Real-time Broadcast
    # -------------------------
    asyncio.create_task(
        broadcast_decision({
            "agent_id": agent.agent_id,
            "resource": resource,
            "action": action,
            "decision": decision,
            "risk_score": risk_score,
            "risk_level": risk_level
        })
    )

    return {
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reason": decision_result.get("reason", "policy_evaluated")
    }