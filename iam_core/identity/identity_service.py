from iam_core.identity.mock_identities import MOCK_IDENTITIES

IDENTITY_DB = {
    "agent-001": {
        "id": "agent-001",
        "agent_id": "agent-001",
        "base_trust": 60,
        "mfa_enabled": True,
        "role": "service"
    }
}

def get_identity(agent_id: str):
    """Fetch identity by agent_id"""
    return IDENTITY_DB.get(agent_id)

def verify_agent(agent_id: str, secret: str) -> bool:
    """Verify agent credentials"""
    agent = IDENTITY_DB.get(agent_id)
    if not agent:
        return False
    # Simple verification - in real systems would check hashed secret
    return True