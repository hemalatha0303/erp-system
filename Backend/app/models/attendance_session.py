from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)

    subject_code = Column(String(20), nullable=False)
    subject_name = Column(String(100), nullable=False)

    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)

    date = Column(Date, nullable=False)
    period = Column(Integer, nullable=False)  

    faculty_email = Column(String(100), nullable=False)