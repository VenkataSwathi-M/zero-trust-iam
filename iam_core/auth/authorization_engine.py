# iam_core/authz/authorization_engine.py

from iam_core.auth.rbac_engine import RBACEngine
from iam_core.auth.abac_engine import ABACEngine

class AuthorizationEngine:
    def __init__(self):
        self.rbac = RBACEngine()
        self.abac = ABACEngine()

    def authorize(self, subject, action, resource, context):
        if not self.rbac.evaluate(subject["role"], action):
            return False, "RBAC denied"

        if not self.abac.evaluate(subject, resource, context):
            return False, "ABAC denied"

        if context.get("risk_score", 0) > 0.7:
            return False, "High risk (PBAC)"

        return True, "Access granted"