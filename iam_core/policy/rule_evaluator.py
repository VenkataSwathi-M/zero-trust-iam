from iam_core.policy.rules import RULES


class RuleEvaluator:
    """
    Evaluates policy rules against the policy context.
    Returns all matched rules (Zero Trust: deny can coexist with allow).
    """

    def evaluate(self, context: dict):
        matched_rules = []

        for rule in RULES:
            try:
                if rule["condition"](context):
                    matched_rules.append(rule)
            except Exception as e:
                # Defensive: rule errors should not crash PDP
                print(f"[RuleEvaluator] Rule {rule.get('id')} failed: {e}")

        return matched_rules