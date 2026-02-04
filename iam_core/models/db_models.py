from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True)
    trust_score = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AccessDecision(Base):
    __tablename__ = "access_decisions"

    id = Column(String, primary_key=True)
    agent_id = Column(String)
    resource = Column(String)
    action = Column(String)
    decision = Column(String)
    risk_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())