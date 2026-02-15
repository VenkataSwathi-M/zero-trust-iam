# iam_core/db/models.py

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    Integer,
    Text,
)
from sqlalchemy.sql import func
from iam_core.db.database import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func, Text

class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.agent_id"), index=True, nullable=False)

    credential_id = Column(Text, nullable=False)  # base64url string
    public_key = Column(Text, nullable=False)     # PEM/COSE (library stores as text)
    sign_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ===============================
# AGENTS
# ===============================

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    trust_level = Column(Float, default=0.5)  # 0–1 normalized
    max_access = Column(String, default="read")
    mfa_enabled = Column(Boolean, default=True)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ===============================
# TRUST SCORE (0–100 SCALE)
# ===============================

class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, unique=True, index=True, nullable=False)
    score = Column(Float, default=50.0)  # 0–100 scale
    updated_at = Column(DateTime, default=datetime.utcnow)


class TrustHistory(Base):
    __tablename__ = "trust_history"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(String, default="event")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ===============================
# TRUST SIGNALS (Advanced signals)
# ===============================

class TrustSignal(Base):
    __tablename__ = "trust_signals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, index=True, nullable=False)

    category = Column(String, nullable=False)  # AUTH / SESSION / ACCESS / TXN / DEVICE
    signal_type = Column(String, nullable=False)

    success = Column(Boolean, nullable=True)
    count = Column(Integer, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    pattern = Column(String, nullable=True)

    trust_delta = Column(Float, default=0.0)
    details = Column(Text, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ===============================
# ACCESS DECISIONS
# ===============================

class AccessDecision(Base):
    __tablename__ = "access_decisions"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)

    resource = Column(String)
    action = Column(String)

    decision = Column(String)  # ALLOW / DENY / STEP_UP
    risk_score = Column(Float)
    risk_level = Column(String)
    pattern = Column(String, default="NONE")
    reason = Column(Text, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ===============================
# AUDIT LOGS
# ===============================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    event_type = Column(String)
    message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ===============================
# BANKING
# ===============================
class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    from_owner = Column(String)
    to_owner = Column(String)

    txn_type = Column(String, default="DEBIT")     # ✅ new
    amount = Column(Float)
    status = Column(String, default="SUCCESS")

    description = Column(Text, default="")         # ✅ new
    created_at = Column(DateTime, default=datetime.utcnow)
    
class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)  # Agent_01
    owner_name = Column(String)
    account_no = Column(String, unique=True)
    ifsc = Column(String, default="ZTIA0001234")
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class BankBeneficiary(Base):
    __tablename__ = "bank_beneficiaries"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)  # who saved this beneficiary
    name = Column(String)
    account_no = Column(String)
    ifsc = Column(String, default="ZTIA0001234")
    is_new = Column(Boolean, default=True)  # new beneficiary => risk
    created_at = Column(DateTime, default=datetime.utcnow)
# ===============================
# POLICIES
# ===============================

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=True)

    agent_id = Column(String, index=True, default="ALL")

    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)
    effect = Column(String, default="ALLOW")

    min_trust = Column(Float, default=0.0)
    max_risk = Column(String, default="HIGH")
    max_amount = Column(Float, nullable=True)
    require_mfa = Column(Boolean, default=False)

    active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())