from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from iam_core.db.database import get_db
from iam_core.db.models import Agent, BankAccount, BankTransaction
from iam_core.auth.deps import get_current_identity

# reuse your agentic decision endpoint logic by importing function OR copy the minimal decision logic
from iam_core.risk.risk_engine import risk_score_from_trust, risk_level
from iam_core.risk.patterns import detect_pattern
from iam_core.agents.anomaly_agent import should_block
from iam_core.policy.policy_reasoner import PolicyReasoner

router = APIRouter(prefix="/banking", tags=["Banking"])
policy = PolicyReasoner()

def enforce_zero_trust(db: Session, agent: Agent, resource: str, action: str):
    trust = float(agent.trust_level)
    score = risk_score_from_trust(trust)
    level = risk_level(score)
    pattern = detect_pattern(resource, action, trust)

    # anomaly agent block
    block, why = should_block(pattern, level, trust)
    if block:
        return ("DENY", f"anomaly_agent:{why}", score, level, pattern)

    # policy reasoner
    out = policy.decide(db=db, agent_id=agent.agent_id, trust=trust, resource=resource, action=action, pattern=pattern)
    decision = out["decision"]
    reason = out.get("reason", "policy")

    # admin max access cap
    if agent.max_access == "read" and action in ["write", "insert", "update", "transfer"]:
        decision = "DENY"
        reason = "max_access_read_only"

    return (decision, reason, score, level, pattern)

@router.get("/accounts")
def read_accounts(identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(401, "Agent not found")

    decision, reason, *_ = enforce_zero_trust(db, agent, "banking_db", "read")
    if decision != "ALLOW":
        raise HTTPException(403, {"decision": decision, "reason": reason})

    rows = db.query(BankAccount).all()
    return [{"id": r.id, "owner": r.owner, "balance": r.balance} for r in rows]

@router.post("/accounts")
def insert_account(payload: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(401, "Agent not found")

    decision, reason, *_ = enforce_zero_trust(db, agent, "banking_db", "insert")
    if decision != "ALLOW":
        raise HTTPException(403, {"decision": decision, "reason": reason})

    owner = payload.get("owner")
    balance = float(payload.get("balance", 0))
    row = BankAccount(id=str(uuid.uuid4()), owner=owner, balance=balance)
    db.add(row)
    db.commit()
    return {"status": "created", "id": row.id}

@router.put("/accounts/{acc_id}")
def update_account(acc_id: str, payload: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(401, "Agent not found")

    decision, reason, *_ = enforce_zero_trust(db, agent, "banking_db", "update")
    if decision != "ALLOW":
        raise HTTPException(403, {"decision": decision, "reason": reason})

    row = db.query(BankAccount).filter(BankAccount.id == acc_id).first()
    if not row:
        raise HTTPException(404, "Account not found")

    row.balance = float(payload.get("balance", row.balance))
    db.commit()
    return {"status": "updated"}

@router.post("/transfer")
def transfer(payload: dict, identity=Depends(get_current_identity), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == identity["sub"]).first()
    if not agent:
        raise HTTPException(401, "Agent not found")

    decision, reason, *_ = enforce_zero_trust(db, agent, "transactions", "transfer")
    if decision != "ALLOW":
        # record denied transaction too (optional)
        tx = BankTransaction(
            id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            from_owner=agent.agent_id,
            to_owner=str(payload.get("to_owner", "unknown")),
            amount=float(payload.get("amount", 0)),
            status="DENIED"
        )
        db.add(tx)
        db.commit()
        raise HTTPException(403, {"decision": decision, "reason": reason})

    tx = BankTransaction(
        id=str(uuid.uuid4()),
        agent_id=agent.agent_id,
        from_owner=agent.agent_id,
        to_owner=str(payload.get("to_owner", "unknown")),
        amount=float(payload.get("amount", 0)),
        status="SUCCESS"
    )
    db.add(tx)
    db.commit()
    return {"status": "SUCCESS", "tx_id": tx.id}