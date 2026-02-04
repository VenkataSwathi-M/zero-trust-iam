from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from iam_core.policy.policy_engine import evaluate_policy
from iam_core.auth.dependencies import get_current_agent

router = APIRouter()

class AuthorizationRequest(BaseModel):
    action: str
    resource: str

@router.post("/authorize")
def authorize(
    data: AuthorizationRequest,
    agent=Depends(get_current_agent)
):
    decision, reasons = evaluate_policy(
        agent=agent,
        action=data.action,
        resource=data.resource
    )

    if decision == "DENY":
        raise HTTPException(
            status_code=403,
            detail={
                "decision": "DENY",
                "reasons": reasons
            }
        )

    return {
        "agent": agent["sub"],
        "action": data.action,
        "resource": data.resource,
        "decision": decision,
        "reasons": reasons
    }
