class AnomalyAgent:
    def detect(self, session):
        if session.get("failed_attempts", 0) > 3:
            return True
        if session.get("geo_change"):
            return True
        return False