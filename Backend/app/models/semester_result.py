from sqlalchemy import Column, Integer, Float, String
from app.core.database import Base

class SemesterResult(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True)

    sid = Column(Integer)
    srno = Column(String(20))
    year = Column(Integer)
    semester = Column(Integer)

    sgpa = Column(Float)
    total_credits = Column(Integer)
    result_status = Column(String(10))  
