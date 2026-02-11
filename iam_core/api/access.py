from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
import asyncio

from iam_core.db.database import get_db
from iam_core.db.models import Agent, AccessDecision, AuditLog, BankTransaction
from iam_core.auth.deps import get_current_identity
from iam_core.policy.policy_reasoner import PolicyReasoner
from iam_core.api.ws import decision_broadcaster

from iam_core.risk.risk_engine import RiskAssessmentEngine
from iam_core.risk.patterns import detect_pattern
from iam_core.agents.anomaly_agent import should_block

router = APIRouter(tags=["Access"])
policy = PolicyReasoner()
risk_engine = RiskAssessmentEngine()

class AccessRequest(BaseModel):
    resource: str   # database/files/transactions
    action: str     # read/write/transfer
    metadata: dict = {}

@router.post("/agentic-decision")
def agentic_decision(
    req: AccessRequest,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(403, "Agent not found")

    if hasattr(agent, "active") and agent.active is False:
        raise HTTPException(403, "Agent blocked")

    trust = float(agent.trust_level)
    risk_score = round(1 - trust, 2)
    risk_level = risk_engine.classify_risk(risk_score)

    pattern = detect_pattern(req.resource, req.action, trust)

    # ✅ PASTE anomaly block EXACTLY HERE
    block, why = should_block(pattern, risk_level, trust)
    if block:
        decision = "DENY"
        reason = f"anomaly_agent:{why}"
    else:
        out = policy.decide(
            db=db,
            agent_id=agent.agent_id,
            trust=trust,
            resource=req.resource,
            action=req.action,
            pattern=pattern
        )
        decision = out["decision"]
        reason = out.get("reason", "policy_reasoner")

    # Admin cap enforcement
    if agent.max_access == "read" and req.action in ["write", "transfer", "delete", "upload"]:
        decision = "DENY"
        reason = "max_access_read_only"

    row = AccessDecision(
        id=str(uuid.uuid4()),
        agent_id=agent.agent_id,
        resource=req.resource,
        action=req.action,
        decision=decision,
        risk_score=risk_score,
        risk_level=risk_level,
        pattern=pattern,
        reason=reason,
    )
    db.add(row)

    if decision == "DENY":
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            event_type="ACCESS_DENY",
            message=f"{req.resource}:{req.action} denied ({reason})"
        ))

    if req.resource == "transactions" and req.action == "transfer":
        amount = float(req.metadata.get("amount", 0))
        to_owner = req.metadata.get("to", "unknown")
        status = "SUCCESS" if decision == "ALLOW" else "DENIED"
        db.add(BankTransaction(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            from_owner=agent.agent_id,
            to_owner=to_owner,
            amount=amount,
            status=status
        ))

    db.commit()

    asyncio.create_task(decision_broadcaster.broadcast({
        "event": "ACCESS_DECISION",
        "agent_id": agent.agent_id,
        "resource": req.resource,
        "action": req.action,
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "pattern": pattern,
        "trust": trust,
        "reason": reason,
    }))

    return {
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "pattern": pattern,
        "trust": trust,
        "reason": reason,
    }