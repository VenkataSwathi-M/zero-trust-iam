from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from iam_core.auth.jwt_utils import decode_access_token
from iam_core.session.session_store import get_session

security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    sid = payload.get("sid")
    if not sid:
        raise HTTPException(status_code=401, detail="Missing session id")

    session = get_session(sid)
    if not session or not session.get("active"):
        raise HTTPException(status_code=401, detail="Session revoked")

    return payload

# ✅ alias (because some files import require_admin)
def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return get_current_admin(credentials)