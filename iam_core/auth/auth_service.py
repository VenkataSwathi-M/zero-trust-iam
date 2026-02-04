from datetime import timedelta
from iam_core.auth.jwt_utils import create_access_token
from iam_core.session.session_store import create_session

ACCESS_TOKEN_EXPIRE_MINUTES = 30

AGENT_DB = {
    "agent-001": {
        "secret": "agent-secret",
        "role": "service"
    }
}

def authenticate_agent(agent_id: str, secret: str):
    agent = AGENT_DB.get(agent_id)
    if not agent or agent["secret"] != secret:
        return None

    session_id = create_session(agent_id)

    token = create_access_token(
        data={
            "sub": agent_id,
            "role": agent["role"],
            "sid": session_id
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return token