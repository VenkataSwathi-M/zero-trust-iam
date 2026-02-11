from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from iam_core.db.database import get_db
from iam_core.db.models import AccessDecision, AuditLog, Agent

router = APIRouter(prefix="/admin/metrics", tags=["Admin Metrics"])

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    decisions = db.query(AccessDecision).order_by(desc(AccessDecision.created_at)).limit(200).all()
    audits = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(50).all()
    agents = db.query(Agent).all()

    allow = sum(1 for d in decisions if d.decision == "ALLOW")
    deny = sum(1 for d in decisions if d.decision == "DENY")
    step = sum(1 for d in decisions if d.decision == "STEP_UP")

    return {
        "agents": [{"agent_id": a.agent_id, "trust": float(a.trust_level)} for a in agents],
        "decision_counts": {"ALLOW": allow, "DENY": deny, "STEP_UP": step},
        "latest_decisions": [
            {
                "agent_id": d.agent_id,
                "resource": d.resource,
                "action": d.action,
                "decision": d.decision,
                "risk_score": float(d.risk_score),
                "created_at": str(d.created_at),
            } for d in decisions
        ],
        "incidents": [
            {
                "agent_id": a.agent_id,
                "event_type": a.event_type,
                "message": a.message,
                "created_at": str(a.created_at),
            } for a in audits
        ]
    }

@router.get("/risk-history/{agent_id}")
def risk_history(agent_id: str, db: Session = Depends(get_db)):
    rows = db.query(AccessDecision)\
        .filter(AccessDecision.agent_id == agent_id)\
        .order_by(AccessDecision.created_at)\
        .limit(200).all()

    return [{"t": str(r.created_at), "risk": float(r.risk_score), "decision": r.decision} for r in rows]