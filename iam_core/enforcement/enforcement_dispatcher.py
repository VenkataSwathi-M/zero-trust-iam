# iam_core/enforcement/enforcement_dispatcher.py

from sqlalchemy.orm import Session

from iam_core.api.ws import decision_broadcaster
from iam_core.audit.attack_trace_store import save_trace
from iam_core.trust.trust_service import update_trust

ENFORCEMENT_LOG = []


class EnforcementDispatcher:
    async def dispatch(self, enforcement_rules, subject_id, context, db: Session):
        """
        enforcement_rules: list of rules {action: BLOCK/REQUIRE_MFA/ALLOW}
        subject_id: agent_id
        context: info dict
        db: SQLAlchemy Session (REQUIRED)
        """
        results = []

        for rule in enforcement_rules:
            action = rule.get("action")

            # ✅ Trust feedback (0..1 scale deltas)
            if action == "BLOCK":
                new_trust = update_trust(db, subject_id, -0.30, reason="ENFORCE_BLOCK")
            elif action == "REQUIRE_MFA":
                new_trust = update_trust(db, subject_id, -0.10, reason="ENFORCE_REQUIRE_MFA")
            elif action == "ALLOW":
                new_trust = update_trust(db, subject_id, +0.02, reason="ENFORCE_ALLOW")
            else:
                new_trust = context.get("trust_score")

            ENFORCEMENT_LOG.append(
                {
                    "subject": subject_id,
                    "action": action,
                    "risk": context.get("risk_level"),
                    "trust": new_trust,
                }
            )

            save_trace(
                subject_id,
                {
                    "signals": context.get("signals"),
                    "risk": context.get("risk_score"),
                    "trust": context.get("trust_score"),
                    "decision": action,
                },
            )

            # ✅ WebSocket broadcast
            await decision_broadcaster.broadcast(
                {
                    "event": "ACCESS_DECISION",
                    "agent_id": subject_id,      # use agent_id consistently
                    "decision": action,
                    "risk_score": context.get("risk_score"),
                    "risk_level": context.get("risk_level"),
                    "trust": new_trust,
                    "timestamp": context.get("timestamp"),
                }
            )

            results.append(action)

        db.commit()

        return {
            "status": "ENFORCED",
            "subject": subject_id,
            "actions": results,
        }