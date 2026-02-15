# iam_core/session/session_store.py
import uuid
import math
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional

DECAY_RATE = 0.015  # trust decay per minute
SESSION_DB: Dict[str, Dict[str, Any]] = {}


def now_utc():
    return datetime.now(timezone.utc)


def create_session(identity_id: str, payload: dict) -> str:
    """
    Creates a session and RETURNS sid.
    payload = token-like dict (sub, role, email, trust, max_access, etc.)
    """
    sid = str(uuid.uuid4())
    SESSION_DB[sid] = {
        "identity_id": identity_id,
        "payload": payload,  # ✅ keep naming consistent everywhere
        "created_at": now_utc(),
        "last_activity": now_utc(),
        "active": True,
        "step_up": False,  # fingerprint/WebAuthn completed?
        "trust_score": float(payload.get("trust", 0.5)),  # base 0..1
        "webauthn": {},  # store challenge/options temporarily
    }
    return sid


def get_session(sid: str) -> Optional[dict]:
    return SESSION_DB.get(sid)


def update_activity(sid: str):
    if sid in SESSION_DB:
        SESSION_DB[sid]["last_activity"] = now_utc()


def revoke_session(sid: str):
    if sid in SESSION_DB:
        SESSION_DB[sid]["active"] = False


def set_step_up(sid: str, ok: bool = True):
    if sid in SESSION_DB:
        SESSION_DB[sid]["step_up"] = bool(ok)


def get_effective_trust(sid: str) -> float:
    """
    Effective trust = trust_score * exp(-DECAY_RATE * minutes_since_last_activity)
    """
    s = SESSION_DB.get(sid)
    if not s:
        return 0.0

    base = float(s.get("trust_score", 0.5))
    last = s.get("last_activity") or s.get("created_at") or now_utc()
    mins = (now_utc() - last).total_seconds() / 60.0

    decayed = base * math.exp(-DECAY_RATE * max(0.0, mins))
    return max(0.0, min(1.0, decayed))


def _push_trust_ws(sid: str, source: str, reason: str):
    """
    Push trust update over websocket (best-effort).
    Uses local import to avoid circular dependency.
    """
    try:
        from iam_core.api.ws_trust import broadcast_trust  # local import

        s = SESSION_DB.get(sid) or {}
        payload = s.get("payload") or {}
        eff = get_effective_trust(sid)

        asyncio.create_task(
            broadcast_trust(
                sid,
                {
                    "type": "TRUST_UPDATE",
                    "sid": sid,
                    "agent_id": payload.get("sub") or s.get("identity_id"),
                    "trust_score": float(s.get("trust_score", 0.5)),
                    "effective_trust": eff,
                    "max_access": payload.get("max_access", "read"),
                    "step_up": bool(s.get("step_up", False)),
                    "reason": reason,
                    "source": source,
                    "time": now_utc().isoformat(),
                },
            )
        )
    except Exception:
        # don't crash request if websocket is down
        pass


def boost_trust(sid: str, reason: str = "manual", delta: float = 0.02) -> float:
    """
    Increase session trust_score and broadcast. Returns new trust_score.
    """
    s = SESSION_DB.get(sid)
    if not s:
        return 0.0

    cur = float(s.get("trust_score", 0.5))
    newv = max(0.0, min(1.0, cur + float(delta)))
    s["trust_score"] = newv
    s["last_activity"] = now_utc()

    _push_trust_ws(sid, source="boost_trust", reason=reason)
    return newv


def penalize_trust(sid: str, reason: str = "risk", delta: float = 0.05) -> float:
    """
    Decrease session trust_score and broadcast. Returns new trust_score.
    """
    s = SESSION_DB.get(sid)
    if not s:
        return 0.0

    cur = float(s.get("trust_score", 0.5))
    newv = max(0.0, min(1.0, cur - float(delta)))
    s["trust_score"] = newv
    s["last_activity"] = now_utc()

    _push_trust_ws(sid, source="penalize_trust", reason=reason)
    return newv


# ✅ backward compatible alias (if older code calls bump_trust)
def bump_trust(sid: str, delta: float):
    return boost_trust(sid, reason="bump_trust", delta=delta)