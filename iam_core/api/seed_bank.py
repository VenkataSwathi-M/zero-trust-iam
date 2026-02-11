from iam_core.db.database import SessionLocal
from iam_core.db.models import BankAccount
import uuid

db = SessionLocal()

if db.query(BankAccount).count() == 0:
    db.add(BankAccount(id=str(uuid.uuid4()), owner="alice", balance=5000))
    db.add(BankAccount(id=str(uuid.uuid4()), owner="bob", balance=2500))
    db.commit()
    print("Seeded bank accounts ✅")
else:
    print("Already seeded ✅")

db.close()