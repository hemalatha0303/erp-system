from sqlalchemy import Column, Integer, String, Date, Text
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_email = Column(String(100), unique=True, nullable=False)

    roll_no = Column(String(20))
    first_name = Column(String(50))
    last_name = Column(String(50))
    gender = Column(String(10))
    blood_group = Column(String(5))
    date_of_birth = Column(Date)
    mobile_no = Column(String(15))
    parent_mobile_no = Column(String(15))
    address = Column(Text)
    parentname = Column(String(100))

    residence_type = Column(String(20))  
    
