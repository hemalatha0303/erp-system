from sqlalchemy import Column, Integer, String, Date, Text
from app.core.database import Base

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    user_email = Column(String(100), unique=True, nullable=False)

    first_name = Column(String(50))
    last_name = Column(String(50))
    gender = Column(String(10))
    blood_group = Column(String(5))
    date_of_birth = Column(Date)
    mobile_no = Column(String(15))
    address = Column(Text)

    qualification = Column(String(100))
    experience = Column(Integer)
