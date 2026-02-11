import json
import time

OTP_TTL = 300  # 5 minutes

def store_otp(redis_client, agent_id: str, decision_id: str, otp: str):
    key = f"otp:{agent_id}:{decision_id}"
    value = {
        "otp": otp,
        "created_at": time.time()
    }
    redis_client.setex(key, OTP_TTL, json.dumps(value))


def get_otp(redis_client, agent_id: str, decision_id: str):
    key = f"otp:{agent_id}:{decision_id}"
    return redis_client.get(key)


def delete_otp(redis_client, agent_id: str, decision_id: str):
    key = f"otp:{agent_id}:{decision_id}"
    redis_client.delete(key)