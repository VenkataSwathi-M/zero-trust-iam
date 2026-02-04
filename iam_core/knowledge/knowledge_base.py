from iam_core.knowledge.attack_patterns import ATTACK_PATTERNS
from iam_core.knowledge.risk_weights import RISK_WEIGHTS
from iam_core.knowledge.history_store import store_event

class SecurityKnowledgeBase:

    def assess_risk(self, signals: dict):
        risk_score = 0

        for signal, value in signals.items():
            weight = RISK_WEIGHTS.get(signal, 0)
            risk_score += weight * value

        risk_score = min(1.0, risk_score)
        risk_level = self.classify_risk(risk_score)

        store_event({
            "signals": signals,
            "risk_score": risk_score,
            "risk_level": risk_level
        })

        return risk_score, risk_level

    def detect_attack_pattern(self, signals):
        detected = []

        for attack, data in ATTACK_PATTERNS.items():
            if any(sig in signals and signals[sig] > 0 for sig in data["signals"]):
                detected.append(attack)

        return detected

    def classify_risk(self, score):
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"