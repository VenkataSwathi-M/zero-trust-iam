from datetime import datetime

DECAY_RATE = 5        # trust points per hour
MIN_TRUST = 20

def apply_decay(trust_record):
    last = trust_record["last_updated"]
    trust = trust_record["trust"]

    hours_passed = (datetime.utcnow() - last).total_seconds() / 3600
    decay = int(hours_passed * DECAY_RATE)

    new_trust = max(MIN_TRUST, trust - decay)
    return new_trust