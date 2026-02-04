class RBACEngine:
    """
    Role-Based Access Control Engine
    """

    def __init__(self):
        # Role → Allowed actions
        self.role_policies = {
            "admin": ["*"],
            "manager": ["read", "transfer"],
            "user": ["read"],
            "guest": []
        }

    def evaluate(self, subject, action):
        role = subject.get("role")

        if not role:
            return False, "No role assigned"

        allowed_actions = self.role_policies.get(role, [])

        if "*" in allowed_actions:
            return True, "RBAC allow (admin)"

        if action in allowed_actions:
            return True, "RBAC allow"

        return False, f"Action '{action}' not permitted for role '{role}'"