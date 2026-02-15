import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from iam_core.db.database import get_db
from iam_core.auth.deps import get_current_identity
from iam_core.db.models import BankAccount, BankTransaction, AuditLog
from iam_core.security.access_guard import require_access
from iam_core.session.session_store import bump_trust

router = APIRouter(prefix="/banking/transfer", tags=["Banking-Transfer"])

@router.post("")
def transfer(req: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    amount = float(req.get("amount", 0))
    to_account = str(req.get("to_account", "")).strip()

    if not to_account or amount <= 0:
        raise HTTPException(400, "to_account and amount required")

    # transfer requires transfer access + higher trust
    trust_min = 0.70 if amount > 10000 else 0.60
    require_access(db, identity, required="transfer", reason=f"Transfer ₹{amount} to {to_account}", trust_min=trust_min)

    agent_id = identity["sub"]
    acc = db.query(BankAccount).filter(BankAccount.agent_id == agent_id).first()
    if not acc:
        raise HTTPException(404, "Account not found")
    if float(acc.balance) < amount:
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            event_type="TRANSFER_DENY",
            message=f"Insufficient funds ₹{amount} to {to_account}"
        ))
        db.commit()
        raise HTTPException(400, "Insufficient balance")

    acc.balance = float(acc.balance) - amount
    txn = BankTransaction(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        from_owner=agent_id,
        to_owner=to_account,
        amount=amount,
        status="SUCCESS",
        created_at=datetime.utcnow(),
    )
    db.add(txn)
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        event_type="TRANSFER_SUCCESS",
        message=f"Transfer ₹{amount} to {to_account}"
    ))
    db.commit()

    bump_trust(identity["sid"], +0.03)  # good action increases trust

    return {"ok": True, "txn_id": txn.id, "balance": float(acc.balance)}