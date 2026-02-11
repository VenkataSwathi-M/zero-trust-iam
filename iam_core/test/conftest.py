import pytest
from fastapi.testclient import TestClient
from iam_core.api.main import app
from iam_core.auth.jwt_utils import create_access_token
from iam_core.trust.trust_store import TRUST_HISTORY
from iam_core.session.session_store import SESSION_DB
from iam_core.metrics.store import METRICS

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Reset in-memory stores before each test"""
    TRUST_HISTORY.clear()
    SESSION_DB.clear()
    # Reset metrics
    METRICS["transactions"] = 0
    METRICS["denied"] = 0
    METRICS["trust_scores"] = []
    METRICS["high_risk"] = 0
    METRICS["policy_denials"] = 0
    yield
    TRUST_HISTORY.clear()
    SESSION_DB.clear()
    METRICS["transactions"] = 0
    METRICS["denied"] = 0
    METRICS["trust_scores"] = []
    METRICS["high_risk"] = 0
    METRICS["policy_denials"] = 0

# -------------------------
# Normal agent token
# -------------------------
@pytest.fixture
def token(client):
    response = client.post(
        "/login",
        json={
            "agent_id": "agent-001",
            "secret": "agent-secret"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# -------------------------
# Admin token
# -------------------------
@pytest.fixture
def admin_token(client):
    response = client.post(
        "/login",
        json={
            "agent_id": "agent-001",
            "secret": "agent-secret"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]