# iam_core/db/seed_banking_data.py
import uuid
import random
from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from iam_core.db.database import SessionLocal, engine, Base
from iam_core.db.models import Agent, BankAccount, BankBeneficiary, BankTransaction, AuditLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def u():  # uuid helper
    return str(uuid.uuid4())


def seed_agents(db: Session):
    # ✅ change emails if you want (must be UNIQUE)
    agents = [
        {"agent_id": "Agent_11", "email": "agent11.demo@gmail.com", "password": "123456"},
        {"agent_id": "Agent_12", "email": "agent12.demo@gmail.com", "password": "123456"},
        {"agent_id": "Agent_13", "email": "agent13.demo@gmail.com", "password": "123456"},
    ]

    for a in agents:
        existing = db.query(Agent).filter(Agent.agent_id == a["agent_id"]).first()
        if not existing:
            db.add(Agent(
                agent_id=a["agent_id"],
                email=a["email"],
                hashed_password=pwd_context.hash(a["password"]),
                trust_level=round(random.uniform(0.55, 0.95), 2),
                max_access=random.choice(["read", "write", "transfer"]),
                mfa_enabled=True,
                active=True,
            ))
    db.commit()


def seed_accounts(db: Session):
    # one bank account per agent
    accounts = [
        {"agent_id": "Agent_11", "owner_name": "Swathi Reddy", "account_no": "621001234567", "ifsc": "ZTIA0001234", "balance": 85432.75},
        {"agent_id": "Agent_12", "owner_name": "Karthik N",     "account_no": "621009876543", "ifsc": "ZTIA0001234", "balance": 12500.00},
        {"agent_id": "Agent_13", "owner_name": "Ayesha S",      "account_no": "621006666999", "ifsc": "ZTIA0001234", "balance": 239990.10},
    ]

    for acc in accounts:
        existing = db.query(BankAccount).filter(BankAccount.account_no == acc["account_no"]).first()
        if not existing:
            db.add(BankAccount(
                id=u(),
                agent_id=acc["agent_id"],
                owner_name=acc["owner_name"],
                account_no=acc["account_no"],
                ifsc=acc["ifsc"],
                balance=float(acc["balance"]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 500)),
            ))
    db.commit()


def seed_beneficiaries(db: Session):
    # beneficiaries per agent (some new => risk)
    ben_templates = [
        ("Ravi Kumar", "622001111222", "HDFC0001245"),
        ("Meena R",    "622003333444", "ICIC0000456"),
        ("SBI Self",   "622005555666", "SBIN0000123"),
        ("Rent Owner", "622007777888", "AXIS0000789"),
        ("Mom",        "622009999000", "KKBK0000678"),
    ]

    for agent_id in ["Agent_11", "Agent_12", "Agent_13"]:
        for i, (name, acc, ifsc) in enumerate(ben_templates):
            exists = db.query(BankBeneficiary).filter(
                BankBeneficiary.agent_id == agent_id,
                BankBeneficiary.account_no == acc
            ).first()
            if not exists:
                db.add(BankBeneficiary(
                    id=u(),
                    agent_id=agent_id,
                    name=name,
                    account_no=acc,
                    ifsc=ifsc,
                    is_new=True if i < 2 else False,   # first 2 are "new"
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 120)),
                ))
    db.commit()


def seed_transactions(db: Session):
    # realistic txns: salaries, UPI, bill pay, transfers
    merchants = [
        ("Amazon", "SUCCESS"),
        ("Swiggy", "SUCCESS"),
        ("Electricity Bill", "SUCCESS"),
        ("UPI Transfer", "SUCCESS"),
        ("ATM Cash", "SUCCESS"),
        ("Netflix", "SUCCESS"),
        ("Failed Transfer", "FAILED"),
    ]

    for agent_id in ["Agent_11", "Agent_12", "Agent_13"]:
        # only add if none exist
        if db.query(BankTransaction).filter(BankTransaction.agent_id == agent_id).first():
            continue

        now = datetime.utcnow()
        for k in range(25):
            m, status = random.choice(merchants)
            amount = round(random.uniform(50, 12000), 2)

            # add a few big transfers
            if k in (5, 12):
                m = "Bank Transfer"
                amount = round(random.uniform(15000, 65000), 2)

            db.add(BankTransaction(
                id=u(),
                agent_id=agent_id,
                from_owner=agent_id,
                to_owner=m,
                amount=float(amount),
                status=status,
                created_at=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            ))

        db.add(AuditLog(
            id=u(),
            agent_id=agent_id,
            event_type="DATA_SEEDED",
            message="Seeded banking account + beneficiaries + transactions",
        ))

    db.commit()


def main():
    # ensures tables exist (if you deleted db, this recreates)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_agents(db)
        seed_accounts(db)
        seed_beneficiaries(db)
        seed_transactions(db)
        print("✅ Seed completed: Agents + Accounts + Beneficiaries + Transactions")
    finally:
        db.close()


if __name__ == "__main__":
    main()