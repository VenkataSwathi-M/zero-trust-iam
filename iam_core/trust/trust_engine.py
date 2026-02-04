from sqlalchemy.orm import Session
from iam_core.db.models import Agent


def update_trust(agent: Agent, decision: str, db: Session):
    """
    Continuous Trust Update (Zero Trust)
    Trust range: 0.0 – 1.0
    """

    if decision == "ALLOW":
        agent.trust_level = min(1.0, agent.trust_level + 0.02)

    elif decision == "DENY":
        agent.trust_level = max(0.0, agent.trust_level - 0.05)

    elif decision == "STEP_UP":
        agent.trust_level = max(0.0, agent.trust_level - 0.02)

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent.trust_level


def classify_risk(trust_level: float):
    if trust_level >= 0.7:
        return "LOW"
    elif trust_level >= 0.4:
        return "MEDIUM"
    else:
        return "HIGH"