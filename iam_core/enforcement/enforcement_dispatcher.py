from iam_core.trust.trust_service import update_trust
from iam_core.api.ws import decision_broadcaster
from iam_core.audit.attack_trace_store import save_trace
from iam_core.db.models import Agent, TrustHistory
ENFORCEMENT_LOG = []


class EnforcementDispatcher:

    async def dispatch(self, enforcement_rules, subject_id, context):
        results = []

        for rule in enforcement_rules:
            action = rule["action"]

            # ---- Trust feedback ----
            if action == "BLOCK":
                new_trust = update_trust(subject_id, -30)
            elif action == "REQUIRE_MFA":
                new_trust = update_trust(subject_id, -10)
            elif action == "ALLOW":
                new_trust = update_trust(subject_id, +2)
            else:
                new_trust = context.get("trust_score")

            # ---- Audit log ----
            ENFORCEMENT_LOG.append({
                "subject": subject_id,
                "action": action,
                "risk": context.get("risk_level"),
                "trust": new_trust
            })

            save_trace(subject_id, {
                "signals": context.get("signals"),
                "risk": context.get("risk_score"),
                "trust": context.get("trust_score"),
                "decision": action,
            })

            # ---- WebSocket broadcast ----
            await decision_broadcaster.broadcast({
                "event": "ACCESS_DECISION",
                "subject": subject_id,
                "decision": action,
                "risk": context.get("risk_score"),
                "trust": new_trust,
                "timestamp": context.get("timestamp"),
            })

            results.append(action)

        return {
            "status": "ENFORCED",
            "subject": subject_id,
            "actions": results
        }