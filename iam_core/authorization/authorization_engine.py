# iam_core/authorization/authorization_engine.py

def authorize(trust_score, risk):
    """
    Zero Trust Policy Decision Point
    """

    if risk == "HIGH":
        return "DENY"

    if risk == "MEDIUM" and trust_score < 50:
        return "DENY"

    return "ALLOW"
