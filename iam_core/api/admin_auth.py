from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import uuid

from iam_core.auth.jwt_utils import create_access_token
from iam_core.session.session_store import create_session  # you must have this
from iam_core.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])

class AdminLoginReq(BaseModel):
    email: str
    password: str

@router.post("/login")
def admin_login(data: AdminLoginReq, db: Session = Depends(get_db)):
    if data.email != "swathi22092004@gmail.com" or data.password != "1234567":
        raise HTTPException(401, "Invalid admin credentials")

    # ✅ create session and get session_id
    sid = create_session(identity_id=data.email)

    # ✅ put sid inside token payload
    token = create_access_token({"sub": data.email, "role": "admin", "sid": sid})

    return {"access_token": token, "token_type": "bearer"}