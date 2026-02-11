# iam_core/db/models.py
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text
from sqlalchemy.sql import func
from datetime import datetime
from iam_core.db.database import Base


class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    trust_level = Column(Float, default=0.5)
    max_access = Column(String, default="read")  # read/write/transfer
    mfa_enabled = Column(Boolean, default=True)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)  # "ALL" for global
    resource = Column(String)
    action = Column(String)
    effect = Column(String)  # ALLOW / DENY / STEP_UP
    min_trust = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AccessDecision(Base):
    __tablename__ = "access_decisions"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)

    resource = Column(String)
    action = Column(String)

    decision = Column(String)       # ALLOW / DENY / STEP_UP
    risk_score = Column(Float)
    risk_level = Column(String)
    pattern = Column(String, default="NONE")
    reason = Column(Text, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    event_type = Column(String)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(String, primary_key=True)
    owner = Column(String, index=True)
    balance = Column(Float, default=0.0)


class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)

    from_owner = Column(String)
    to_owner = Column(String)
    amount = Column(Float)
    status = Column(String)  # SUCCESS / DENIED

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ✅ REQUIRED for trust_service imports
class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, unique=True, index=True, nullable=False)
    score = Column(Float, default=50.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class TrustHistory(Base):
    __tablename__ = "trust_history"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    old_score = Column(Float)
    new_score = Column(Float)
    reason = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())