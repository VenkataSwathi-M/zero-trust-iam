from fastapi import APIRouter
from iam_core.enforcement.enforcement_dispatcher import ENFORCEMENT_LOG
from iam_core.trust.trust_store import TRUST_HISTORY

router = APIRouter()

@router.get("/dashboard/stats")
def dashboard_stats():
    allowed = sum(1 for r in ENFORCEMENT_LOG if r["action"] == "ALLOW")
    denied = sum(1 for r in ENFORCEMENT_LOG if r["action"] == "BLOCK")
    mfa = sum(1 for r in ENFORCEMENT_LOG if r["action"] == "REQUIRE_MFA")

    return {
        "total_requests": len(ENFORCEMENT_LOG),
        "allowed": allowed,
        "denied": denied,
        "mfa": mfa
    }


@router.get("/decisions")
def recent_decisions():
    return [
        {
            "id": i,
            "decision": r["action"],
            "risk": r["risk_level"],
            "trust_score": TRUST_HISTORY.get(r["subject"], [{}])[-1].get("trust", 50)
        }
        for i, r in enumerate(ENFORCEMENT_LOG[-20:])
    ]