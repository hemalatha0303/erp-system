from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.core.database import Base

class HODProfile(Base):
    __tablename__ = "hod"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    personal_email = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    mobile_no = Column(String(15))
    address = Column(Text)
    qualification = Column(String(100))
    experience = Column(Integer)
    branch = Column(String(20))
