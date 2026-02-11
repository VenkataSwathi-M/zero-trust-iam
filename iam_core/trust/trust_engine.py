from typing import Dict
from sqlalchemy.orm import Session
from iam_core.db.models import Agent, TrustHistory
class TrustEngine:
    """
    Zero Trust Engine
    Uses DB-backed trust score (0.0 – 1.0)
    """

    def calculate_trust(
        self,
        agent_id: str,
        context: Dict,
        db: Session
    ) -> float:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            raise ValueError("Agent not found")

        old_score = agent.trust_level
        score = old_score

        # ---- Context signals ----
        if context.get("device_trusted"):
            score += 0.05

        if context.get("location_known"):
            score += 0.03

        if context.get("recent_login"):
            score += 0.02

        risk = context.get("risk_level", "low")
        if risk == "medium":
            score -= 0.1
        elif risk == "high":
            score -= 0.25

        # Clamp 0–1
        score = max(0.0, min(1.0, score))

        # Persist
        agent.trust_level = score
        db.add(agent)

        db.add(TrustHistory(
            agent_id=agent.agent_id,
            old_score=old_score,
            new_score=score,
            reason="context_update"
        ))

        db.commit()
        return score

    def is_access_allowed(
        self,
        agent_id: str,
        db: Session,
        threshold: float = 0.6
    ) -> bool:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            return False
        return agent.trust_level >= threshold


# ✅ Singleton instance
trust_engine = TrustEngine()


# 🔹 Simple helper for login / enforcement
def update_trust(agent_id: str, delta: float, reason: str, db):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return

    old = agent.trust_level
    new = max(0, min(1, old + delta))

    agent.trust_level = new

    history = TrustHistory(
        agent_id=agent_id,
        old_score=old,
        new_score=new,
        reason=reason
    )

    db.add(history)
    db.commit()