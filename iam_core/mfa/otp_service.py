import time
import random

OTP_TTL = 300  # 5 minutes
_OTP_STORE = {}  # {(agent_id, decision_id): (otp, expires_at)}

def generate_otp(agent_id: str, decision_id: str) -> str:
    otp = str(random.randint(100000, 999999))
    expires_at = time.time() + OTP_TTL
    _OTP_STORE[(agent_id, decision_id)] = (otp, expires_at)
    return otp

def validate_otp(agent_id: str, decision_id: str, otp_input: str) -> bool:
    key = (agent_id, decision_id)

    if key not in _OTP_STORE:
        return False

    otp, expires_at = _OTP_STORE[key]

    if time.time() > expires_at:
        del _OTP_STORE[key]
        return False

    if otp != otp_input:
        return False

    del _OTP_STORE[key]  # one-time use
    return True