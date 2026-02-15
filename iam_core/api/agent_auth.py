from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import random
import uuid
import os

from iam_core.db.database import get_db
from iam_core.db.models import Agent, AuditLog, TrustHistory
from iam_core.auth.jwt_utils import create_access_token
from iam_core.services.mailer import send_otp_email
from iam_core.session.session_store import create_session, bump_trust

router = APIRouter(prefix="/agent/auth", tags=["Agent Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OTP_TTL_MIN = 5
OTP_DB = {}  # sid -> {agent_id, otp, expires_at, attempts}

class SendOtpReq(BaseModel):
    agent_id: str
    password: str

class VerifyOtpReq(BaseModel):
    sid: str
    otp: str

def now_utc():
    return datetime.now(timezone.utc)

@router.post("/send-otp")
def send_otp(data: SendOtpReq, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid agent_id or password")

    if not pwd_context.verify(data.password, agent.hashed_password):
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=data.agent_id,
            event_type="LOGIN_FAIL",
            message="Agent login failed (wrong password)"
        ))
        agent.trust_level = max(0.0, float(agent.trust_level) - 0.05)
        db.add(TrustHistory(agent_id=agent.agent_id, score=float(agent.trust_level), reason="login_fail"))
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid agent_id or password")

    # ✅ create session and return sid
    sid = create_session(
        identity_id=agent.agent_id,
        payload={"sub": agent.agent_id, "role": "agent", "trust": float(agent.trust_level)}
    )

    otp = str(random.randint(100000, 999999))
    OTP_DB[sid] = {
        "agent_id": agent.agent_id,
        "otp": otp,
        "expires_at": now_utc() + timedelta(minutes=OTP_TTL_MIN),
        "attempts": 0,
    }

    if not agent.email:
        raise HTTPException(status_code=400, detail="No email configured for this agent")

    mode = os.getenv("OTP_MODE", "TERMINAL").upper()  # ✅ default terminal
    if mode == "TERMINAL":
        print(f"\n✅ OTP for {agent.agent_id} ({agent.email}) = {otp}  (valid {OTP_TTL_MIN} min)\n")
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            event_type="OTP_PRINTED",
            message="OTP printed to terminal (dev fallback)"
        ))
        db.commit()
        return {"message": "OTP printed in server terminal", "sid": sid, "ttl_minutes": OTP_TTL_MIN}

    # PROD email mode
    try:
        send_otp_email(agent.email, otp)
    except Exception as e:
        # fallback to terminal if email fails
        print(f"\n⚠️ EMAIL FAILED, OTP for {agent.agent_id} = {otp}. Error: {e}\n")
        return {"message": "Email failed, OTP printed in terminal", "sid": sid, "ttl_minutes": OTP_TTL_MIN}

    db.add(AuditLog(
        id=str(uuid.uuid4()),
        agent_id=agent.agent_id,
        event_type="OTP_SENT",
        message=f"OTP sent to {agent.email}"
    ))
    db.commit()

    return {"message": "OTP sent successfully", "sid": sid, "ttl_minutes": OTP_TTL_MIN}

@router.post("/verify-otp")
def verify_otp(data: VerifyOtpReq, db: Session = Depends(get_db)):
    rec = OTP_DB.get(data.sid)
    if not rec:
        raise HTTPException(status_code=400, detail="OTP not found. Request OTP again.")

    if now_utc() > rec["expires_at"]:
        OTP_DB.pop(data.sid, None)
        raise HTTPException(status_code=400, detail="OTP expired. Request OTP again.")

    rec["attempts"] += 1
    if rec["attempts"] > 5:
        OTP_DB.pop(data.sid, None)
        raise HTTPException(status_code=429, detail="Too many OTP attempts.")

    if data.otp != rec["otp"]:
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=rec["agent_id"],
            event_type="OTP_FAIL",
            message="OTP verification failed"
        ))
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid OTP")

    OTP_DB.pop(data.sid, None)

    agent = db.query(Agent).filter(Agent.agent_id == rec["agent_id"]).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.trust_level = min(1.0, float(agent.trust_level) + 0.02)
    db.add(TrustHistory(agent_id=agent.agent_id, score=float(agent.trust_level), reason="mfa_success"))
    db.add(AuditLog(id=str(uuid.uuid4()), agent_id=agent.agent_id, event_type="LOGIN_SUCCESS", message="OTP verified"))

    # ✅ token includes sid (required)
    token = create_access_token({
        "sub": agent.agent_id,
        "role": "agent",
        "trust": float(agent.trust_level),
        "sid": data.sid,
    })

    db.commit()

    return {"access_token": token, "token_type": "bearer", "agent_id": agent.agent_id, "sid": data.sid}