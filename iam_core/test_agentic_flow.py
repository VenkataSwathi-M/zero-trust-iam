def test_agentic_feedback():
    from iam_core.feedback.feedback_engine import FeedbackEngine

    engine = FeedbackEngine()
    result = engine.apply("agent-001", "DENY", 0.8)

    assert result["trust_delta"] < 0