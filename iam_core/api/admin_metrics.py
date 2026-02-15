# iam_core/api/admin_metrics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from iam_core.db.database import get_db
from iam_core.db.models import AccessDecision, AuditLog, Agent, TrustHistory
from iam_core.auth.admin_deps import require_admin   # ✅ add this

router = APIRouter(prefix="/admin/metrics", tags=["Admin Metrics"])

@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),   # ✅ protect
):
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
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in decisions
        ],
        "incidents": [
            {
                "agent_id": a.agent_id,
                "event_type": a.event_type,
                "message": a.message,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in audits
        ],
    }

@router.get("/risk-history/{agent_id}")
def risk_history(
    agent_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),   # ✅ protect
):
    rows = (
        db.query(AccessDecision)
        .filter(AccessDecision.agent_id == agent_id)
        .order_by(AccessDecision.created_at)
        .limit(200)
        .all()
    )
    return [{"t": r.created_at.isoformat() if r.created_at else None,
             "risk": float(r.risk_score), "decision": r.decision} for r in rows]

@router.get("/trust-history/{agent_id}")
def trust_history(
    agent_id: str,
    limit: int = 60,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),   # ✅ protect
):
    rows = (
        db.query(TrustHistory)
        .filter(TrustHistory.agent_id == agent_id)
        .order_by(desc(TrustHistory.created_at))
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    return [{"t": r.created_at.isoformat() if r.created_at else None,
             "trust": float(r.score), "reason": r.reason} for r in rows]