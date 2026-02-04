class ABACEngine:
    """
    Attribute-Based Access Control Engine
    """

    def evaluate(self, subject, resource, context):

        # Owner-based access
        if resource.get("owner"):
            if subject.get("id") != resource.get("owner"):
                return False, "Not resource owner"

        # Time-based access
        hour = context.get("hour")
        if hour and (hour < 8 or hour > 20):
            return False, "Outside business hours"

        # Location-based
        if context.get("location") == "untrusted":
            return False, "Untrusted location"

        # Department match
        if subject.get("department") != resource.get("department"):
            return False, "Department mismatch"

        # Risk-aware ABAC
        if context.get("risk_level") == "HIGH":
            return False, "High risk environment"

        return True, "ABAC conditions satisfied"