from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from iam_core.auth.jwt_utils import decode_access_token
from iam_core.session.session_store import get_session, update_activity, get_effective_trust

security = HTTPBearer()

def get_current_identity(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    role = payload.get("role")
    if role not in ("agent", "service", "admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    sid = payload.get("sid")
    if not sid:
        raise HTTPException(status_code=401, detail="Missing session id")

    session = get_session(sid)
    if not session or not session.get("active"):
        raise HTTPException(status_code=401, detail="Session revoked")

    update_activity(sid)

    # attach computed trust
    payload["effective_trust"] = get_effective_trust(sid)
    payload["step_up"] = bool(session.get("step_up"))
    return payload

def require_identity(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return get_current_identity(credentials)