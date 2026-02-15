from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from iam_core.db.database import get_db
from iam_core.auth.deps import get_current_identity
from iam_core.db.models import BankAccount, BankTransaction
from iam_core.security.access_guard import require_access

router = APIRouter(prefix="/banking/read", tags=["Banking-Read"])

@router.get("/me")
def my_account(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    require_access(db, identity, required="read", reason="Reading account overview", trust_min=0.45)

    agent_id = identity["sub"]
    acc = db.query(BankAccount).filter(BankAccount.agent_id == agent_id).first()
    if not acc:
        raise HTTPException(404, "Bank account not found")

    return {
        "agent_id": acc.agent_id,
        "owner_name": acc.owner_name,
        "account_no": acc.account_no,
        "ifsc": acc.ifsc,
        "balance": float(acc.balance),
        "currency": "INR",
        "available_balance": float(acc.balance),
        "branch": getattr(acc, "branch", "Main Branch"),
        "last_login": None,
        "account_type": "Savings",
        "customer_name": acc.owner_name,
    }

@router.get("/transactions")
def my_transactions(limit: int = 10, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    require_access(db, identity, required="read", reason="Viewing transactions", trust_min=0.45)

    agent_id = identity["sub"]
    rows = (
        db.query(BankTransaction)
        .filter(BankTransaction.agent_id == agent_id)
        .order_by(desc(BankTransaction.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "date": r.created_at.isoformat() if r.created_at else "",
            "description": r.to_owner,
            "category": "Transfer",
            "type": "DEBIT",
            "amount": float(r.amount),
            "status": r.status,
        }
        for r in rows
    ]