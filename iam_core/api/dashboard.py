from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.enforcement.enforcement_dispatcher import ENFORCEMENT_LOG

from iam_core.trust.trust_service import get_trust_metrics
from iam_core.trust.trust_store import TrustStore

router = APIRouter(prefix="/admin", tags=["Dashboard"])

trust_store = TrustStore()

# -------------------------------
# Dashboard Stats (IN-MEMORY)
# -------------------------------
@router.get("/dashboard/stats")
def dashboard_stats():
    allowed = sum(1 for r in ENFORCEMENT_LOG if r["action"] == "ALLOW")
    denied = sum(1 for r in ENFORCEMENT_LOG if r["action"] == "BLOCK")
    mfa = sum(1 for r in ENFORCEMENT_LOG if r["action"] == "REQUIRE_MFA")

    return {
        "total_requests": len(ENFORCEMENT_LOG),
        "allowed": allowed,
        "denied": denied,
        "mfa": mfa,
    }


# -------------------------------
# Recent Decisions (FIXED)
# -------------------------------
@router.get("/dashboard/decisions")
def recent_decisions():
    results = []

    for i, r in enumerate(ENFORCEMENT_LOG[-20:]):
        subject = r.get("subject")

        trust_score = (
            trust_store.get_trust(subject)
            if subject else 50
        )

        results.append({
            "id": i,
            "decision": r["action"],
            "risk": r.get("risk_level"),
            "trust_score": trust_score,
        })

    return results


# -------------------------------
# DB-backed metrics
# -------------------------------
@router.get("/dashboard/db-stats")
def dashboard_db_stats(db: Session = Depends(get_db)):
    from iam_core.db.models import AccessDecision

    total = db.query(AccessDecision).count()
    allowed = db.query(AccessDecision).filter_by(decision="allow").count()
    denied = total - allowed

    return {
        "total_requests": total,
        "allowed": allowed,
        "denied": denied,
    }


# -------------------------------
# Trust Metrics
# -------------------------------
@router.get("/dashboard/metrics")
def dashboard_metrics():
    return {
        "trust": get_trust_metrics(),
        "enforcement_log": ENFORCEMENT_LOG[-50:],
    }