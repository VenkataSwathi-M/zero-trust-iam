from sqlalchemy import Column, String, DateTime
from datetime import datetime, timedelta
from database import Base

class MFAOtp(Base):
    __tablename__ = "mfa_otps"

    agent_id = Column(String, primary_key=True)
    decision_id = Column(String, primary_key=True)
    otp = Column(String)
    expires_at = Column(DateTime)