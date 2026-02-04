class SecurityKnowledgeBase:
    """
    Stores security intelligence & historical risk patterns
    """

    def __init__(self):
        self.event_profiles = {
            "auth_failed": {
                "severity": "MEDIUM",
                "trust_decay": 0.2
            },
            "access_denied": {
                "severity": "HIGH",
                "trust_decay": 0.3
            },
            "anomaly_detected": {
                "severity": "HIGH",
                "trust_decay": 0.4
            },
            "session_abuse": {
                "severity": "CRITICAL",
                "trust_decay": 0.5
            }
        }

    def get_event_profile(self, event_type):
        return self.event_profiles.get(
            event_type,
            {
                "severity": "LOW",
                "trust_decay": 0.1
            }
        )