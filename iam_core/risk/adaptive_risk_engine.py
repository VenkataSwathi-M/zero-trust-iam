class AdaptiveRiskEngine:
    """
    Risk engine with reinforcement-style weight adaptation
    """

    def __init__(self):
        self.weights = {
            "auth_fail": 0.25,
            "deny": 0.20,
            "trust_decay": 0.20,
            "anomaly": 0.25,
            "session_abuse": 0.10
        }

        self.learning_rate = 0.05   # slow + stable learning

    def calculate_risk(self, signals):
        risk = sum(
            self.weights[k] * signals.get(k, 0)
            for k in self.weights
        )
        return round(min(max(risk, 0), 1), 2)

    def adapt_weights(self, signals, decision):
        """
        Reinforce signals that led to correct decisions
        """

        for signal, value in signals.items():
            if value == 0:
                continue

            if decision == "DENY":
                # reinforce important risk indicators
                self.weights[signal] += self.learning_rate

            elif decision == "ALLOW":
                # weaken false-positive contributors
                self.weights[signal] -= self.learning_rate / 2

        self._normalize_weights()

    def _normalize_weights(self):
        total = sum(self.weights.values())
        for k in self.weights:
            self.weights[k] = round(self.weights[k] / total, 3)