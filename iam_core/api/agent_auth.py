from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from iam_core.db.database import get_db
from iam_core.db.models import Agent
from iam_core.security.passwords import verify_password
from iam_core.mfa.otp_service import generate_otp, validate_otp
from iam_core.security.email_service import send_otp_email
from iam_core.security.jwt import create_access_token

router = APIRouter(prefix="/agent/auth", tags=["Agent Auth"])

@router.post("/login")
def agent_login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(400, "Email and password required")

    agent = db.query(Agent).filter(Agent.email == email).first()
    if not agent or not verify_password(password, agent.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    if hasattr(agent, "active") and not agent.active:
        raise HTTPException(403, "Agent is blocked/inactive")

    decision_id = str(uuid.uuid4())
    otp = generate_otp(agent.agent_id, decision_id)

    # ✅ don’t crash login if email fails
    try:
        send_otp_email(agent.email, otp)
    except Exception as e:
        print("[EMAIL ERROR]", e)
        print(f"[DEV OTP] OTP for {agent.email}: {otp}")

    return {"message": "OTP generated", "decision_id": decision_id}

@router.post("/verify-otp")
def verify_agent_otp(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    otp = payload.get("otp")
    decision_id = payload.get("decision_id")

    if not email or not otp or not decision_id:
        raise HTTPException(400, "email, otp, decision_id required")

    agent = db.query(Agent).filter(Agent.email == email).first()
    if not agent:
        raise HTTPException(404, "Agent not found")

    ok = validate_otp(agent.agent_id, decision_id, otp)
    if not ok:
        raise HTTPException(401, "Invalid/expired OTP")

    token = create_access_token({
        "sub": agent.agent_id,
        "role": "agent",
        "trust": agent.trust_level,
    })

    return {"access_token": token, "token_type": "bearer"}