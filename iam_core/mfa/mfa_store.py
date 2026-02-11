import time

OTP_STORE = {}

def store_otp(agent_id, decision_id, otp):
    OTP_STORE[(agent_id, decision_id)] = {
        "otp": otp,
        "expires_at": time.time() + 60,
        "attempts": 0
    }

def verify_otp(agent_id, decision_id, otp):
    key = (agent_id, decision_id)
    record = OTP_STORE.get(key)

    if not record:
        return False, "OTP_NOT_FOUND"

    if time.time() > record["expires_at"]:
        del OTP_STORE[key]
        return False, "OTP_EXPIRED"

    if record["attempts"] >= 3:
        del OTP_STORE[key]
        return False, "MAX_ATTEMPTS_EXCEEDED"

    record["attempts"] += 1

    if record["otp"] != otp:
        return False, "INVALID_OTP"

    del OTP_STORE[key]
    return True, "VERIFIED"