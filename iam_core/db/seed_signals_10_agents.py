import uuid
import random
from datetime import datetime, timedelta

from iam_core.db.database import SessionLocal
from iam_core.db.models import Agent, TrustHistory, AccessDecision, AuditLog, TrustSignal

# ---------- helpers ----------
def classify_risk(score: float) -> str:
    if score < 0.35:
        return "LOW"
    if score < 0.70:
        return "MEDIUM"
    return "HIGH"

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def now_minus(minutes: int):
    return datetime.utcnow() - timedelta(minutes=minutes)

# ---------- signal templates ----------
# trust_delta: + increases trust, - decreases trust
SIGNALS = [
    # AUTH signals
    ("AUTH", "AUTH_LOGIN_SUCCESS", True,  +0.02, "Login success"),
    ("AUTH", "AUTH_LOGIN_FAIL",    False, -0.12, "Repeated login failure"),
    ("AUTH", "AUTH_MFA_SUCCESS",   True,  +0.03, "MFA success"),
    ("AUTH", "AUTH_MFA_FAIL",      False, -0.10, "MFA failure"),
    ("AUTH", "AUTH_PASSWORD_RESET",None,  -0.06, "Password reset / recovery"),
    ("AUTH", "AUTH_NEW_DEVICE",    None,  -0.08, "New device login"),

    # SESSION signals
    ("SESSION", "SESSION_IDLE_LONG",      None, -0.05, "Idle time high"),
    ("SESSION", "SESSION_LONG_SESSION",   None, -0.04, "Very long session"),
    ("SESSION", "SESSION_TOKEN_REUSE",    None, -0.30, "Token reuse from new IP/device"),

    # ACCESS pattern signals
    ("ACCESS", "ACCESS_UNUSUAL_ENDPOINT", None, -0.07, "Unusual endpoint usage"),
    ("ACCESS", "ACCESS_RATE_SPIKE",       None, -0.10, "Sudden request spike"),
    ("ACCESS", "ACCESS_HIGH_PRIV_ACTION", None, -0.12, "High privilege action"),
    ("ACCESS", "ACCESS_NIGHT_ACCESS",     None, -0.06, "Outside normal time window"),

    # TXN signals
    ("TXN", "TXN_AMOUNT_SPIKE",     None, -0.12, "Transfer amount > avg"),
    ("TXN", "TXN_NEW_BENEFICIARY",  None, -0.08, "New / unknown beneficiary"),
    ("TXN", "TXN_MANY_TRANSFERS",   None, -0.10, "Many transfers in short window"),

    # DEVICE
    ("DEVICE", "DEVICE_FINGERPRINT_MISMATCH", None, -0.20, "Device fingerprint mismatch"),
]

def pick_pattern(category, signal_type):
    if signal_type in ["TXN_AMOUNT_SPIKE", "TXN_MANY_TRANSFERS", "TXN_NEW_BENEFICIARY"]:
        return "TRANSFER_ATTEMPT"
    if signal_type == "ACCESS_HIGH_PRIV_ACTION":
        return "DESTRUCTIVE_ACTION"
    if signal_type == "SESSION_TOKEN_REUSE":
        return "TOKEN_REUSE"
    return "NONE"

def seed(reset=False):
    db = SessionLocal()
    try:
        if reset:
            db.query(TrustSignal).delete()
            db.query(AccessDecision).delete()
            db.query(TrustHistory).delete()
            db.query(AuditLog).delete()
            db.query(Agent).delete()
            db.commit()

        # ---------- create 10 agents ----------
        agents = []
        for i in range(1, 11):
            agent_id = f"Agent_{i:02d}"   # Agent_01 .. Agent_10
            email = f"agent{i:02d}@demo.com"
            # You can keep any hashed_password; demo only
            a = Agent(
                agent_id=agent_id,
                email=email,
                hashed_password="$2b$12$demoHashedPasswordForSeedOnlyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                trust_level=round(random.uniform(0.40, 0.90), 2),
                max_access=random.choice(["read", "write", "transfer"]),
                mfa_enabled=True,
                active=True,
            )
            agents.append(a)
            db.add(a)
        db.commit()

        # ---------- for each agent insert MAX 15 signal rows ----------
        for a in agents:
            trust = float(a.trust_level)
            base_minutes = random.randint(30, 600)

            # choose 15 signals (mix good + bad)
            chosen = random.sample(SIGNALS, k=15)

            for idx, (category, signal_type, success, trust_delta, msg) in enumerate(chosen):
                minutes_ago = base_minutes - idx * random.randint(5, 25)
                created_at = now_minus(max(1, minutes_ago))

                # risk_score derived mainly from badness
                # (strong negative trust_delta => higher risk)
                raw_risk = clamp(abs(min(0.0, trust_delta)) * 4 + random.uniform(0.0, 0.25), 0, 1)
                risk_level = classify_risk(raw_risk)
                pattern = pick_pattern(category, signal_type)

                # extra fields
                count = None
                if "FAIL" in signal_type:
                    count = random.randint(1, 6)
                if "MANY_TRANSFERS" in signal_type or "RATE_SPIKE" in signal_type:
                    count = random.randint(5, 30)

                details = msg
                if signal_type == "SESSION_TOKEN_REUSE":
                    details += " | ip_changed=true device_changed=true"
                if signal_type == "AUTH_NEW_DEVICE":
                    details += " | device=new_android"
                if signal_type.startswith("TXN_"):
                    details += f" | amount={round(random.uniform(500, 9000),2)}"

                # store signal
                db.add(TrustSignal(
                    agent_id=a.agent_id,
                    category=category,
                    signal_type=signal_type,
                    success=success,
                    count=count,
                    risk_score=float(round(raw_risk, 2)),
                    risk_level=risk_level,
                    pattern=pattern,
                    trust_delta=float(trust_delta),
                    details=details,
                    created_at=created_at,
                ))

                # update trust and store trust history point
                trust = clamp(trust + trust_delta, 0.0, 1.0)

                db.add(TrustHistory(
                    agent_id=a.agent_id,
                    score=float(round(trust, 2)),
                    reason=signal_type,
                    created_at=created_at,
                ))

                # create AccessDecision for ACCESS/TXN signals (so risk chart fills)
                if category in ["ACCESS", "TXN"]:
                    resource = "transactions" if category == "TXN" else "accounts"
                    action = "transfer" if category == "TXN" else random.choice(["read", "write", "delete"])

                    # decision logic
                    decision = "ALLOW"
                    reason = "normal"
                    if signal_type in ["ACCESS_HIGH_PRIV_ACTION"] and trust < 0.65:
                        decision = "DENY"
                        reason = "high_priv_low_trust"
                    elif category == "TXN" and trust < 0.60:
                        decision = "STEP_UP"
                        reason = "txn_low_trust_stepup"
                    elif risk_level == "HIGH" and trust < 0.50:
                        decision = random.choice(["DENY", "STEP_UP"])
                        reason = "risk_high"

                    db.add(AccessDecision(
                        id=str(uuid.uuid4()),
                        agent_id=a.agent_id,
                        resource=resource,
                        action=action,
                        decision=decision,
                        risk_score=float(round(raw_risk, 2)),
                        risk_level=risk_level,
                        pattern=pattern,
                        reason=reason,
                        created_at=created_at,
                    ))

                    # audit log on deny/step_up
                    if decision in ["DENY", "STEP_UP"]:
                        db.add(AuditLog(
                            id=str(uuid.uuid4()),
                            agent_id=a.agent_id,
                            event_type=f"ACCESS_{decision}",
                            message=f"{resource}:{action} -> {decision} ({reason})",
                            created_at=created_at,
                        ))

            # ✅ keep agent.trust_level synced to latest trust
            a.trust_level = float(round(trust, 2))
            db.add(a)

        db.commit()
        print("✅ Seeded 10 agents with 15 trust inputs each (signals + history + decisions + audits).")

    finally:
        db.close()

if __name__ == "__main__":
    # set reset=True once if you want clean seed
    seed(reset=False)