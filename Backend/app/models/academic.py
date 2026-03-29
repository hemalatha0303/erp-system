from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base

class Academic(Base):
    __tablename__ = "academics"

    academic_id = Column(Integer, primary_key=True)
    sid = Column(Integer)
    user_email = Column(String(100))
    srno = Column(String(20))

    branch = Column(String(20))
    batch = Column(String(20))
    course = Column(String(20))
    year = Column(Integer)
    semester = Column(Integer)
    section = Column(String(5))
    type = Column(String(20))
    quota = Column(String(20))

    admission_date = Column(Date)
    status = Column(String(20))
