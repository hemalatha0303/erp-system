from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("attendance_sessions.id"))
    sid = Column(Integer, nullable=False)
    srno = Column(String(20), nullable=False)

    status = Column(String(10), nullable=False)  
