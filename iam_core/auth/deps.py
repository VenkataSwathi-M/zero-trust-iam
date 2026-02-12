from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from iam_core.security.jwt import verify_access_token
security = HTTPBearer(auto_error=False)

def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization token")

    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token") # ✅ MUST verify using same module as create_access_token


    return payload