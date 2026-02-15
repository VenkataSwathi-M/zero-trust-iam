import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.auth.jwt_utils import create_access_token
from iam_core.db.models import AuditLog
from iam_core.session.session_store import create_session

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])

class AdminLoginReq(BaseModel):
    email: str
    password: str

@router.post("/login")
def admin_login(data: AdminLoginReq, db: Session = Depends(get_db)):
    if data.email != "swathi22092004@gmail.com" or data.password != "1234567":
        raise HTTPException(401, "Invalid admin credentials")

    sid = create_session(identity_id=data.email, payload={"sub": data.email, "role": "admin", "trust": 1.0})

    token = create_access_token({"sub": data.email, "role": "admin", "sid": sid})

    db.add(AuditLog(
        id=str(uuid.uuid4()),
        agent_id=data.email,
        event_type="ADMIN_LOGIN",
        message="Admin logged in successfully"
    ))
    db.commit()

    return {"access_token": token, "token_type": "bearer", "sid": sid}