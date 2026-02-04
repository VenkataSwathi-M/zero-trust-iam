
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# -------- Core imports --------
from iam_core.api.dashboard import router as dashboard_router
from iam_core.api.access import router as access_router
from iam_core.api.decision_trace import router as trace_router
from iam_core.api.ws import decision_ws
from iam_core.admin.admin_routes import admin_router

from iam_core.auth.jwt_utils import decode_access_token
from iam_core.session.session_store import get_session
from iam_core.policy.policy_reasoner import PolicyReasoner
from iam_core.events.security_event_listener import SecurityEventListener
from iam_core.trust.trust_store import get_trust_history, get_current_trust

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="Zero Trust IAM Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Globals --------
security = HTTPBearer()
policy_engine = PolicyReasoner()
listener = SecurityEventListener()

# -------- Routers --------
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
app.include_router(access_router, prefix="/api", tags=["Access"])
app.include_router(trace_router, prefix="/api", tags=["Decision Trace"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# -------- Health Check --------
@app.get("/health")
def health_check():
    return {"status": "IAM Core running"}

# -------- Auth Helper --------
def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    session = get_session(payload["sid"])
    if not session or not session["active"]:
        raise HTTPException(status_code=401, detail="Session revoked")

    return payload

# -------- Trust APIs --------
@app.get("/trust/{identity_id}")
def trust(identity_id: str):
    return {
        "current_trust": get_current_trust(identity_id),
        "history": get_trust_history(identity_id),
    }

# -------- Agentic Decision API --------
@app.post("/agentic-decision")
def agentic_decision(event: dict, identity=Depends(get_current_identity)):
    return listener.handle_event(
        event_type=event["event_type"],
        metadata={"identity_id": identity["sub"], **event.get("metadata", {})},
    )

# -------- Policy Authorization --------
@app.post("/authorize")
def authorize_policy(request: dict):
    return policy_engine.decide(
        signals=request["signals"],
        risk_score=request["risk_score"],
        risk_level=request["risk_level"],
        metadata=request.get("metadata"),
    )
# ---------------------------
# Dashboard REST API
# ---------------------------
@app.get("/api/dashboard/stats")
def dashboard_stats():
    return {
        "total_requests": 1200,
        "allowed": 980,
        "denied": 180,
        "mfa": 40
    }

# ---------------------------
# WebSocket
# ---------------------------
connections = []

@app.websocket("/ws/decisions")
async def decision_ws(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        connections.remove(websocket)