# iam_core/trust/trust_store.py

from datetime import datetime

TRUST_HISTORY = {}
DEFAULT_TRUST = 50


def update_trust(identity_id, delta):
    history = TRUST_HISTORY.setdefault(identity_id, [])

    last_trust = history[-1]["trust"] if history else DEFAULT_TRUST
    new_trust = max(0, min(100, last_trust + delta))

    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "trust": new_trust,
        "delta": delta
    })

    return new_trust


def get_trust_history(identity_id):
    return TRUST_HISTORY.get(identity_id, [])


def get_current_trust(identity_id):
    history = TRUST_HISTORY.get(identity_id)
    return history[-1]["trust"] if history else DEFAULT_TRUST