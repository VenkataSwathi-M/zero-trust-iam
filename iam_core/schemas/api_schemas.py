from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- Agent ----------
class AgentLoginRequest(BaseModel):
    agent_id: str


class AgentResponse(BaseModel):
    agent_id: str
    trust_score: float

    class Config:
        from_attributes = True


# ---------- Access ----------
class AccessRequest(BaseModel):
    resource: str
    action: str
    context: Optional[dict] = {}


class AccessDecisionResponse(BaseModel):
    agent_id: str
    decision: str
    risk_score: float
    created_at: datetime