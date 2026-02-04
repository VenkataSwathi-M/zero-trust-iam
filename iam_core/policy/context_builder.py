from datetime import datetime

class ContextBuilder:
    """
    Builds a complete Zero Trust policy evaluation context
    """

    def build_context(self, signals, risk_score, risk_level, metadata=None):
        metadata = metadata or {}

        context = {
            # ---------------------------
            # Meta
            # ---------------------------
            "timestamp": datetime.utcnow().isoformat(),

            # ---------------------------
            # Subject (Agent)
            # ---------------------------
            "subject": metadata.get("agent_id"),
            "subject_attrs": {
                "role": signals.get("role", "agent"),
                "trust_level": signals.get("trust_level", 0.5),
                "auth_failures": signals.get("auth_fail", 0),
            },

            # ---------------------------
            # Resource & Action
            # ---------------------------
            "resource_attrs": {
                "resource": metadata.get("resource", "unknown"),
                "sensitivity": metadata.get("sensitivity", "medium"),
            },
            "action": signals.get("action"),

            # ---------------------------
            # Risk Context
            # ---------------------------
            "risk_score": risk_score,
            "risk_level": risk_level,

            # ---------------------------
            # Behavioral Signals
            # ---------------------------
            "signals": {
                "deny_count": signals.get("deny", 0),
                "anomaly": signals.get("anomaly", False),
                "session_abuse": signals.get("session_abuse", False),
                "trust_decay": signals.get("trust_decay", 0),
            },

            # ---------------------------
            # Session Context
            # ---------------------------
            "idle_minutes": metadata.get("idle_minutes", 0),
            "location": metadata.get("location"),
            "device_trust": metadata.get("device_trust"),
            "time_of_day": metadata.get("time_of_day"),

            # ---------------------------
            # Raw Metadata (audit)
            # ---------------------------
            "metadata": metadata,
        }

        return context