from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    user_email = Column(String(100), unique=True, nullable=False)
    personal_email = Column(String(100))

    first_name = Column(String(50))
    last_name = Column(String(50))
    mobile_no = Column(String(15))
    address = Column(Text)

    qualification = Column(String(100))
    experience = Column(Integer)
    
    # Subject and branch information
    subject_code = Column(String(20))
    subject_name = Column(String(100))
    branch = Column(String(20))
