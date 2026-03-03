from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100))
    credits = Column(Integer)
    semester = Column(Integer)
    branch = Column(String(20))
