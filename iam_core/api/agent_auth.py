from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from iam_core.db.database import get_db
from iam_core.db.models import Agent
from iam_core.security.passwords import verify_password
from iam_core.mfa.otp_service import generate_otp, validate_otp
from iam_core.security.email_service import send_otp_email
from iam_core.security.jwt import create_access_token
from iam_core.trust.trust_service import apply_trust_event

router = APIRouter(prefix="/agent/auth", tags=["Agent Auth"])


@router.post("/login")
def agent_login(payload: dict, db: Session = Depends(get_db)):
    agent_id = payload.get("agent_id")
    password = payload.get("password")

    if not agent_id or not password:
        raise HTTPException(status_code=400, detail="agent_id and password required")

    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent or not agent.active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, agent.hashed_password):
        # ✅ FIX: pass event positionally
        apply_trust_event(db, agent.agent_id, "AUTH_FAIL", -0.05, "wrong_password")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    decision_id = str(uuid.uuid4())
    otp = generate_otp(agent.agent_id, decision_id)

    try:
        send_otp_email(agent.email, otp)
    except Exception as e:
        print("[EMAIL ERROR]", e)
        print(f"[DEV OTP] OTP for {agent.email}: {otp}")

    return {"message": "OTP sent", "decision_id": decision_id}


@router.post("/verify-otp")
def verify_agent_otp(payload: dict, db: Session = Depends(get_db)):
    agent_id = payload.get("agent_id")
    otp = payload.get("otp")
    decision_id = payload.get("decision_id")

    if not agent_id or not otp or not decision_id:
        raise HTTPException(status_code=400, detail="agent_id, otp, decision_id required")

    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent or not agent.active:
        raise HTTPException(status_code=404, detail="Agent not found")

    ok = validate_otp(agent.agent_id, decision_id, otp)
    if not ok:
        # ✅ FIX: pass event positionally
        apply_trust_event(db, agent.agent_id, "OTP_FAIL", -0.05, "wrong_otp")
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    # ✅ FIX: pass event positionally
    apply_trust_event(db, agent.agent_id, "OTP_OK", 0.02, "otp_verified")

    # IMPORTANT: refresh agent trust from DB (because apply_trust_event updates it)
    db.refresh(agent)

    if agent.trust_level < 0.4:
        raise HTTPException(status_code=403, detail="Low trust score")

    token = create_access_token({
        "sub": agent.agent_id,
        "role": "agent",
        "trust": agent.trust_level,
    })

    return {"access_token": token, "token_type": "bearer"}