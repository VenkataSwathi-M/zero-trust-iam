import uuid
import math
from datetime import datetime, timezone

DECAY_RATE = 0.015  # policy-controlled trust decay

# In-memory session store (future → Redis / DB)
SESSION_DB = {}


def now_utc():
    return datetime.now(timezone.utc)


def get_effective_trust(session):
    """
    Returns trust score after time-based decay
    NIST ZTA: Continuous verification
    """
    idle_minutes = (
        now_utc() - session["last_activity"]
    ).total_seconds() / 60

    decayed_trust = session["trust_score"] * math.exp(
        -DECAY_RATE * idle_minutes
    )

    return round(max(0, decayed_trust), 2)


def create_session(identity_id: str):
    session_id = str(uuid.uuid4())

    SESSION_DB[session_id] = {
        "identity_id": identity_id,
        "created_at": now_utc(),
        "last_activity": now_utc(),
        "trust_score": 70,   # initial trust baseline
        "active": True
    }

    return session_id


def get_session(session_id: str):
    return SESSION_DB.get(session_id)


def update_session(session_id: str, trust_score: int):
    if session_id in SESSION_DB:
        SESSION_DB[session_id]["trust_score"] = trust_score
        SESSION_DB[session_id]["last_activity"] = now_utc()


def revoke_session(session_id: str):
    if session_id in SESSION_DB:
        SESSION_DB[session_id]["active"] = False
