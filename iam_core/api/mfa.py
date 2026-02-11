from fastapi import APIRouter, HTTPException

from iam_core.mfa.mfa_service import generate_otp, verify_otp
from iam_core.api.ws import decision_broadcaster

router = APIRouter(prefix="/mfa", tags=["MFA"])


@router.post("/request")
async def request_mfa(agent_id: str, decision_id: str):
    generate_otp(agent_id, decision_id)

    await decision_broadcaster.broadcast({
        "event": "MFA_REQUESTED",
        "agent_id": agent_id,
        "decision_id": decision_id
    })

    return {"message": "OTP generated"}


@router.post("/verify")
async def verify_mfa(agent_id: str, decision_id: str, code: str):
    ok, msg = verify_otp(agent_id, decision_id, code)

    if not ok:
        raise HTTPException(status_code=401, detail=msg)

    await decision_broadcaster.broadcast({
        "event": "MFA_VERIFIED",
        "agent_id": agent_id,
        "decision_id": decision_id
    })

    return {"status": "verified"}