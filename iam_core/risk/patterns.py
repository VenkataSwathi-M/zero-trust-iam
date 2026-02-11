def detect_pattern(resource: str, action: str, trust: float):
    # High-risk: transfers, deletes, repeated write
    if resource == "transactions" and action == "transfer":
        return "TRANSFER_ATTEMPT"

    if resource == "files" and action == "delete":
        return "DESTRUCTIVE_ACTION"

    if trust < 0.4:
        return "LOW_TRUST"

    return "NORMAL"