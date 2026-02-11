from iam_core.policy.policies import POLICIES
import fnmatch

def evaluate_policy(agent, action, resource, trust_score: float):
    # STEP-UP first (context-aware rule)
    if action == "transfer" and trust_score < 0.7:
        return "STEP_UP"

    # Normal policy evaluation
    for policy in POLICIES:
        if (
            policy["role"] == agent["role"] and
            policy["action"] == action and
            fnmatch.fnmatch(resource, policy["resource"])
        ):
            return policy["effect"]

    return "DENY"  # Zero Trust default