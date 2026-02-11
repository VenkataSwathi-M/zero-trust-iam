import random
import time

OTP_STORE = {}  # later → Redis

def generate_otp(agent_id, decision_id):
    code = str(random.randint(100000, 999999))
    OTP_STORE[decision_id] = {
        "agent_id": agent_id,
        "code": code,
        "expires": time.time() + 60,
        "attempts": 0
    }
    return code

def verify_otp(agent_id, decision_id, code):
    record = OTP_STORE.get(decision_id)

    if not record:
        return False, "OTP expired"

    if time.time() > record["expires"]:
        OTP_STORE.pop(decision_id, None)
        return False, "OTP expired"

    if record["attempts"] >= 3:
        return False, "Too many attempts"

    record["attempts"] += 1

    if record["code"] != code:
        return False, "Invalid OTP"

    OTP_STORE.pop(decision_id)
    return True, "verified"