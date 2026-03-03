from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from app.core.database import Base
from datetime import datetime

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String(100), nullable=False)
    sender_role = Column(String(50), nullable=False) 
    student_roll = Column(String(50), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="WARNING") # 
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)