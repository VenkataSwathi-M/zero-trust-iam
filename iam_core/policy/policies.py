POLICIES = [
    {
        "role": "service",
        "action": "transfer_funds",
        "resource": "account-*",
        "effect": "ALLOW"
    },
    {
        "role": "service",
        "action": "delete_account",
        "resource": "*",
        "effect": "DENY"
    }
]