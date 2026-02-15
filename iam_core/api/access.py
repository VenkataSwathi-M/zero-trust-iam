# iam_core/api/access.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from iam_core.db.database import get_db
from iam_core.db.models import Agent, AccessDecision, AuditLog, BankTransaction, TrustHistory
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
async def agentic_decision(
    req: dict,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    resource = req.get("resource")
    action = req.get("action")
    metadata = req.get("metadata", {}) or {}

    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(403, "Agent not found")

    if hasattr(agent, "active") and agent.active is False:
        raise HTTPException(403, "Agent blocked")

    # ✅ current trust
    trust = float(agent.trust_level)

    # ✅ base risk
    risk_score = round(1 - trust, 2)
    risk_level = risk_engine.classify_risk(risk_score)

    pattern = detect_pattern(resource, action, trust)

    # ✅ device fingerprint mismatch simulation
    device_fp = metadata.get("device_fp")
    if device_fp:
        if getattr(agent, "device_fp", None) and agent.device_fp != device_fp:
            pattern = "DEVICE_FINGERPRINT_MISMATCH"
            risk_score = min(1.0, risk_score + 0.25)
            risk_level = risk_engine.classify_risk(risk_score)
        elif not getattr(agent, "device_fp", None):
            agent.device_fp = device_fp  # first time bind

    # ✅ transfer risk bump
    if resource == "transactions" and action == "transfer":
        amount = float(metadata.get("amount", 0))
        if amount > 10000:
            risk_score = min(1.0, risk_score + 0.30)
            pattern = "HIGH_AMOUNT_TRANSFER"
            risk_level = risk_engine.classify_risk(risk_score)

    # ✅ auto deny if too risky
    if risk_score > 0.85:
        decision = "DENY"
        reason = "auto_deny_high_risk"
    else:
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

    # ✅ max_access guard
    if agent.max_access == "read" and action in ["write", "transfer", "delete", "upload"]:
        decision = "DENY"
        reason = "max_access_read_only"

    # ✅ store decision row
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

    # ✅ audit logs
    if decision == "DENY":
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            event_type="ACCESS_DENY",
            message=f"{resource}:{action} denied ({reason})"
        ))
    elif decision == "STEP_UP":
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            event_type="ACCESS_STEP_UP",
            message=f"{resource}:{action} -> STEP_UP ({reason})"
        ))

    # ✅ banking transaction insert
    bank_event = None
    if resource == "transactions" and action == "transfer":
        amount = float(metadata.get("amount", 0))
        to_owner = metadata.get("to", "unknown")
        status = "SUCCESS" if decision == "ALLOW" else ("STEP_UP" if decision == "STEP_UP" else "DENIED")

        db.add(BankTransaction(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            from_owner=agent.agent_id,
            to_owner=to_owner,
            amount=amount,
            status=status
        ))

        bank_event = {
            "event": "BANK_TXN",
            "agent_id": agent.agent_id,
            "from_owner": agent.agent_id,
            "to_owner": to_owner,
            "amount": amount,
            "status": status,
            "risk_score": risk_score,
            "pattern": pattern,
        }

    # ✅ TRUST UPDATE (this fixes admin vs agent mismatch)
    if decision == "DENY":
        agent.trust_level = max(0.0, float(agent.trust_level) - 0.10)
    elif decision == "STEP_UP":
        agent.trust_level = max(0.0, float(agent.trust_level) - 0.05)
    elif decision == "ALLOW":
        agent.trust_level = min(1.0, float(agent.trust_level) + 0.02)

    # ✅ TrustHistory insert for chart
    db.add(TrustHistory(
        agent_id=agent.agent_id,
        score=float(agent.trust_level),
        reason=f"decision:{decision}:{pattern}"
    ))

    db.commit()

    # ✅ updated trust after commit
    trust = float(agent.trust_level)

    # ✅ broadcast decision
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

    # ✅ broadcast bank txn feed (optional)
    if bank_event:
        bank_event["trust"] = trust
        await decision_broadcaster.broadcast(bank_event)

    return {
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "pattern": pattern,
        "trust": trust,
        "reason": reason,
    }