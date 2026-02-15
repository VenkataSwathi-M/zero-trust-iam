# iam_core/api/fingerprint.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from iam_core.auth.deps import get_current_identity
from iam_core.session.session_store import set_step_up, boost_trust

router = APIRouter(prefix="/agent/auth", tags=["Fingerprint"])


class FingerReq(BaseModel):
    verified: bool


@router.post("/verify-fingerprint")
def verify_fingerprint(data: FingerReq, identity=Depends(get_current_identity)):
    sid = identity.get("sid")
    if not sid:
        raise HTTPException(status_code=401, detail="Missing session id")

    if data.verified:
        set_step_up(sid, True)
        new_trust = boost_trust(sid, reason="fingerprint_verified", delta=0.30)
        return {"message": "Fingerprint verified", "trust_score": new_trust}

    return {"message": "Fingerprint failed", "trust_score": None}