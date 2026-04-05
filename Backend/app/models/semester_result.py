from sqlalchemy import Column, Integer, Float, String
from app.core.database import Base

class SemesterResult(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True)

    sid = Column(Integer)
    srno = Column(String(20))  # For backward compatibility
    rollno = Column(String(20))  # Roll number
    batch = Column(String(20))  # Batch like 2022-26
    branch = Column(String(20))  # Branch like CSE, CSM, etc.
    section = Column(String(5))  # Section A, B, C
    year = Column(Integer)
    semester = Column(Integer)

    sgpa = Column(Float)  # Semester GPA
    cgpa = Column(Float)  # Cumulative GPA
    total_credits = Column(Integer)
    result_status = Column(String(10))  # PASS/FAIL
