from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.core.database import Base

class ExternalMarks(Base):
    __tablename__ = "external_marks"

    id = Column(Integer, primary_key=True)
    sid = Column(Integer, ForeignKey("students.id"))
    srno = Column(String(20))
    subject_code = Column(String(20))
    subject_name = Column(String(100))
    year = Column(Integer)
    semester = Column(Integer)
    grade = Column(String(2))
    credits = Column(Integer)
    gpa = Column(Float)
    entered_by = Column(String(100))
