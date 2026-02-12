from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

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

@router.post("/agentic-decision")
async def agentic_decision(   # ✅ make async
    req: dict,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    resource = req.get("resource")
    action = req.get("action")
    metadata = req.get("metadata", {})

    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(403, "Agent not found")

    if hasattr(agent, "active") and agent.active is False:
        raise HTTPException(403, "Agent blocked")

    trust = float(agent.trust_level)
    risk_score = round(1 - trust, 2)
    risk_level = risk_engine.classify_risk(risk_score)

    pattern = detect_pattern(resource, action, trust)

    block, why = should_block(pattern, risk_level, trust)
    if block:
        decision = "DENY"
        reason = f"anomaly_agent:{why}"
    else:
        out = policy.decide(
            db=db,
            agent_id=agent.agent_id,
            trust=trust,
            resource=resource,
            action=action,
            pattern=pattern
        )
        decision = out["decision"]
        reason = out.get("reason", "policy_reasoner")

    if agent.max_access == "read" and action in ["write", "transfer", "delete", "upload"]:
        decision = "DENY"
        reason = "max_access_read_only"

    row = AccessDecision(
        id=str(uuid.uuid4()),
        agent_id=agent.agent_id,
        resource=resource,
        action=action,
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
            message=f"{resource}:{action} denied ({reason})"
        ))

    if resource == "transactions" and action == "transfer":
        amount = float(metadata.get("amount", 0))
        to_owner = metadata.get("to", "unknown")
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

    # ✅ NOW SAFE (we have event loop)
    await decision_broadcaster.broadcast({
        "event": "ACCESS_DECISION",
        "agent_id": agent.agent_id,
        "resource": resource,
        "action": action,
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "pattern": pattern,
        "trust": trust,
        "reason": reason,
    })

    return {
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "pattern": pattern,
        "trust": trust,
        "reason": reason,
    }