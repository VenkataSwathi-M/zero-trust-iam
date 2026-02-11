# iam_core/auth/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from iam_core.db.database import get_db
from iam_core.auth.jwt_utils import verify_access_token

security = HTTPBearer()

def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid/expired token")

    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return payload