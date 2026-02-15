# iam_core/security/access_guard.py
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session

from iam_core.db.models import AuditLog, TrustHistory, Agent
from iam_core.session.session_store import get_effective_trust, bump_trust

# access order
ORDER = {"read": 1, "write": 2, "transfer": 3}

def require_access(
    db: Session,
    identity: dict,
    required: str,
    reason: str = "",
    trust_min: float = 0.0,
):
    """
    - Checks agent.max_access (read/write/transfer)
    - Checks trust threshold
    - If violated: logs Audit + TrustHistory, penalizes trust, raises structured 403
    """
    agent_id = identity.get("sub")
    sid = identity.get("sid")

    if not agent_id or not sid:
        raise HTTPException(401, detail="Missing identity/session")

    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, detail="Agent not found")

    agent_access = (agent.max_access or "read").lower().strip()
    required = required.lower().strip()

    eff_trust = get_effective_trust(sid)

    # access check
    if ORDER.get(agent_access, 1) < ORDER.get(required, 1):
        # penalize trust on policy violation attempt
        bump_trust(sid, -0.07)

        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            event_type="ACCESS_DENY",
            message=f"Denied {required} (has {agent_access}). {reason}"
        ))
        db.add(TrustHistory(
            agent_id=agent_id,
            score=max(0.0, eff_trust - 0.07),
            reason=f"deny_{required}"
        ))
        db.commit()

        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCESS_DENIED",
                "message": f"You have '{agent_access}' access only. '{required}' denied.",
                "required": required,
                "current_access": agent_access,
                "trust": eff_trust,
                "reason": reason or "policy",
            }
        )

    # trust check (optional)
    if eff_trust < trust_min:
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            event_type="STEP_UP_REQUIRED",
            message=f"Trust {eff_trust} < {trust_min} for {required}. {reason}"
        ))
        db.commit()
        raise HTTPException(
            status_code=403,
            detail={
                "code": "STEP_UP_REQUIRED",
                "message": f"Low trust ({eff_trust}). Fingerprint required for {required}.",
                "trust": eff_trust,
                "trust_min": trust_min,
                "required": required,
            }
        )

    return {"agent_access": agent_access, "trust": eff_trust}