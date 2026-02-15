from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from iam_core.api.admin_agents import router as admin_agents_router
from iam_core.api.admin_policies import router as admin_policies_router
from iam_core.api.admin_auth import router as admin_auth_router
from iam_core.api.admin_audit import router as admin_audit_router
from iam_core.api.admin_metrics import router as admin_metrics_router

from iam_core.api.agent_auth import router as agent_auth_router
from iam_core.api.access import router as access_router
from iam_core.api.ws import router as ws_router
from iam_core.api.banking import router as banking_router

from iam_core.db.database import engine
from iam_core.db.models import Base
from iam_core.api.fingerprint import router as fingerprint_router
from iam_core.api.session_status import router as session_router
from iam_core.api.banking_read import router as banking_read_router
from iam_core.api.banking_write import router as banking_write_router
from iam_core.api.banking_transfer import router as banking_transfer_router
from iam_core.api.ws_trust import router as ws_trust_router

app = FastAPI(title="Zero Trust IAM Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://192.168.31.211:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ✅ Admin APIs
app.include_router(admin_auth_router)
app.include_router(admin_agents_router)
app.include_router(admin_policies_router)
app.include_router(admin_audit_router)
app.include_router(admin_metrics_router)

# ✅ Agent APIs
app.include_router(agent_auth_router)
app.include_router(access_router)
app.include_router(ws_router)
app.include_router(banking_router)
app.include_router(fingerprint_router)
app.include_router(session_router)
app.include_router(banking_read_router)
app.include_router(banking_write_router)
app.include_router(banking_transfer_router)
app.include_router(ws_trust_router)