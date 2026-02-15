# iam_core/api/banking.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from datetime import datetime

from iam_core.db.database import get_db
from iam_core.auth.deps import get_current_identity
from iam_core.db.models import BankAccount, BankBeneficiary, BankTransaction, AuditLog, Agent
from iam_core.api.ws_banking import banking_broadcaster  # (we create below)
from fastapi import HTTPException
from iam_core.session.session_store import get_session, get_effective_trust

router = APIRouter(prefix="/banking", tags=["Banking"])


def require_step_up_if_needed(identity, reason: str, min_trust: float = 0.6):
    sid = identity.get("sid")
    s = get_session(sid)
    if not s:
        raise HTTPException(401, "Session missing")

    trust = get_effective_trust(sid)
    step_up = bool(s.get("step_up", False))

    if trust < min_trust and not step_up:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "STEP_UP_REQUIRED",
                "message": f"{reason}. Fingerprint verification required (trust={trust})."
            }
        )

@router.post("/profile")
def update_profile(req: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    # simulate write
    return {"message": f"Profile updated for {identity['sub']} (name={req.get('name')}, phone={req.get('phone')})"}

@router.get("/me")
def my_account(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
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
        "created_at": acc.created_at.isoformat() if acc.created_at else None,
    }


@router.get("/beneficiaries")
def beneficiaries(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent_id = identity["sub"]
    rows = (
        db.query(BankBeneficiary)
        .filter(BankBeneficiary.agent_id == agent_id)
        .order_by(desc(BankBeneficiary.created_at))
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "account_no": r.account_no,
            "ifsc": r.ifsc,
            "is_new": bool(r.is_new),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

@router.get("/transactions")
def my_transactions(limit: int = 50, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent_id = identity["sub"]
    rows = (
        db.query(BankTransaction)
        .filter(BankTransaction.agent_id == agent_id)
        .order_by(desc(BankTransaction.created_at))
        .limit(limit)
        .all()
    )
    return [{
    "id": r.id,
    "to_owner": r.to_owner,
    "type": getattr(r, "txn_type", "DEBIT"),
    "amount": float(r.amount),
    "status": r.status,
    "description": getattr(r, "description", "") or "",
    "created_at": r.created_at.isoformat() if r.created_at else None,}
for r in rows
]


@router.post("/transfer")
async def transfer(
    req: dict,
    identity=Depends(get_current_identity),
    db: Session = Depends(get_db)
):
    """
    Realistic transfer endpoint.
    We also write AuditLog + BankTransaction and broadcast to websocket.
    """
    agent_id = identity["sub"]
    to_account = str(req.get("to_account", "")).strip()
    amount = float(req.get("amount", 0))
    note = str(req.get("note", "")).strip()

    if not to_account or amount <= 0:
        raise HTTPException(400, "to_account and amount required")

    acc = db.query(BankAccount).filter(BankAccount.agent_id == agent_id).first()
    if not acc:
        raise HTTPException(404, "Account not found")

    if acc.balance < amount:
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            event_type="TRANSFER_DENY",
            message=f"Insufficient funds transfer ₹{amount} to {to_account}"
        ))
        db.commit()
        raise HTTPException(400, "Insufficient balance")

    # mark beneficiary as new/known
    ben = db.query(BankBeneficiary).filter(
        BankBeneficiary.agent_id == agent_id,
        BankBeneficiary.account_no == to_account
    ).first()

    is_new_beneficiary = True
    if ben:
        is_new_beneficiary = bool(ben.is_new)
        ben.is_new = False  # once used, not new anymore
    else:
        db.add(BankBeneficiary(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            name="Saved Beneficiary",
            account_no=to_account,
            ifsc="ZTIA0001234",
            is_new=True,
        ))

    # ✅ apply realistic rules (risk bump / status)
    status = "SUCCESS"
    risk_tag = "NORMAL"

    if amount > 10000:
        risk_tag = "HIGH_AMOUNT_TRANSFER"
    if is_new_beneficiary:
        risk_tag = "NEW_BENEFICIARY_TRANSFER"

    # Debit
    acc.balance = float(acc.balance) - amount

    txn = BankTransaction(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        from_owner=agent_id,
        to_owner=to_account,
        amount=amount,
        status=status,
        created_at=datetime.utcnow()
    )
    db.add(txn)

    db.add(AuditLog(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        event_type="TRANSFER_SUCCESS",
        message=f"Transfer ₹{amount} to {to_account} ({risk_tag}) {note}"
    ))

    db.commit()

    # ✅ realtime feed
    await banking_broadcaster.broadcast({
        "event": "BANK_TXN",
        "agent_id": agent_id,
        "to": to_account,
        "amount": amount,
        "status": status,
        "risk_tag": risk_tag,
        "time": txn.created_at.isoformat(),
    })

    return {
        "ok": True,
        "balance": float(acc.balance),
        "txn_id": txn.id,
        "risk_tag": risk_tag
    }