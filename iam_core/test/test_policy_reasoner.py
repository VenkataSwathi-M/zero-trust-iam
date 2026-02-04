from iam_core.policy.policy_reasoner import PolicyReasoner


def test_low_risk_allow():
    policy = PolicyReasoner()

    result = policy.decide(
        signals={
            "auth_fail": 0,
            "deny": 0,
            "trust_decay": 0.0,
            "anomaly": 0,
            "session_abuse": 0
        },
        risk_score=0.2,
        risk_level="LOW"
    )

    print("\nLOW RISK RESULT:", result)
    assert result["decision"] == "ALLOW"


def test_anomaly_step_up():
    policy = PolicyReasoner()

    result = policy.decide(
        signals={
            "auth_fail": 0,
            "deny": 0,
            "trust_decay": 0.2,
            "anomaly": 1,
            "session_abuse": 0
        },
        risk_score=0.5,
        risk_level="MEDIUM"
    )

    print("\nANOMALY RESULT:", result)
    assert result["decision"] == "STEP_UP_AUTH"


def test_high_risk_deny():
    policy = PolicyReasoner()

    result = policy.decide(
        signals={
            "auth_fail": 1,
            "deny": 1,
            "trust_decay": 0.5,
            "anomaly": 1,
            "session_abuse": 1
        },
        risk_score=0.85,
        risk_level="HIGH"
    )

    print("\nHIGH RISK RESULT:", result)
    assert result["decision"] == "DENY"