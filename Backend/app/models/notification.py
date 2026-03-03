from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)

    target_role = Column(String(20))  # ALL | STUDENT
    batch = Column(String(20), nullable=True)
    
    # NEW FIELDS
    category = Column(String(50), default="GENERAL") # ACADEMIC, FEES, etc.
    priority = Column(String(20), default="NORMAL")  # CRITICAL, IMPORTANT, NORMAL

    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)