from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from iam_core.api.admin_agents import router as admin_agents_router
from iam_core.api.admin_policies import router as admin_policies_router
from iam_core.api.agent_auth import router as agent_auth_router
from iam_core.api.access import router as access_router
from iam_core.api.dashboard import router as dashboard_router
from iam_core.api.ws import router as ws_router
from iam_core.api.banking import router as banking_router
from iam_core.db.database import engine
from iam_core.db.models import Base
from iam_core.admin.admin_routes import admin_router
from iam_core.api.admin_auth import router as admin_auth_router
app = FastAPI(title="Zero Trust IAM Core")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(admin_agents_router)
app.include_router(admin_policies_router)
app.include_router(agent_auth_router)
app.include_router(access_router)     
app.include_router(dashboard_router)
app.include_router(ws_router)
app.include_router(admin_router)
app.include_router(admin_auth_router)