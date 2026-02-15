import uuid
from iam_core.db.database import SessionLocal
from iam_core.db.models import Policy, AccessDecision, TrustHistory

db = SessionLocal()

# --- policies ---
p1 = Policy(
    id=str(uuid.uuid4()),
    name="Global Transfer Guard",
    agent_id="ALL",
    resource="transactions",
    action="transfer",
    effect="STEP_UP",
    min_trust=0.6,
    max_risk="HIGH",
    max_amount=None,
    require_mfa=True,
    active=True,
    priority=1,
)

db.add(p1)

# --- access decisions ---
db.add_all([
    AccessDecision(id="d1", agent_id="Agent_01", resource="transactions", action="read",
                decision="ALLOW", risk_score=0.12, risk_level="LOW", pattern="NONE", reason="seed"),
    AccessDecision(id="d2", agent_id="Agent_02", resource="transactions", action="transfer",
                decision="STEP_UP", risk_score=0.72, risk_level="HIGH", pattern="TRANSFER_ATTEMPT", reason="seed"),
    AccessDecision(id="d3", agent_id="Agent_03", resource="transactions", action="delete",
                decision="DENY", risk_score=0.91, risk_level="HIGH", pattern="DESTRUCTIVE_ACTION", reason="seed"),
])

# --- trust history ---
db.add_all([
    TrustHistory(agent_id="Agent_01", score=0.60, reason="seed"),
    TrustHistory(agent_id="Agent_02", score=0.45, reason="seed"),
    TrustHistory(agent_id="Agent_03", score=0.80, reason="seed"),
])

db.commit()
db.close()
print("Seed done ✅")