# iam_core/enforcement/dispatcher.py

class EnforcementDispatcher:
    """
    Dispatches enforcement rules to IAM engines
    """

    def dispatch(self, rules, subject=None):
        responses = []

        for rule in rules:
            action = rule["action"]

            if action == "BLOCK":
                responses.append(self._block_access(rule, subject))

            elif action == "REQUIRE_MFA":
                responses.append(self._trigger_step_up(rule, subject))

            elif action == "ALLOW":
                responses.append(self._allow_access(rule, subject))

        return responses

    def _block_access(self, rule, subject):
        return {
            "engine": "AuthorizationEngine",
            "status": "DENIED",
            "subject": subject,
            "details": rule
        }

    def _trigger_step_up(self, rule, subject):
        return {
            "engine": "AuthenticationEngine",
            "status": "STEP_UP_REQUIRED",
            "subject": subject,
            "details": rule
        }

    def _allow_access(self, rule, subject):
        return {
            "engine": "SessionManager",
            "status": "ALLOWED",
            "subject": subject,
            "details": rule
        }