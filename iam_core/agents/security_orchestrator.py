class SecurityOrchestratorAgent:
    def __init__(self, risk_agent, policy_agent, anomaly_agent, enforcement_agent):
        self.risk_agent = risk_agent
        self.policy_agent = policy_agent
        self.anomaly_agent = anomaly_agent
        self.enforcement_agent = enforcement_agent

    def decide(self, identity, action, resource, session):
        context = {}

        context["risk_score"] = self.risk_agent.assess(identity, action, resource)
        context["anomaly"] = self.anomaly_agent.detect(session)
        context["policy_decision"] = self.policy_agent.evaluate(context)

        return self.enforcement_agent.enforce(context)