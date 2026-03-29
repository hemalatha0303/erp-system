from sqlalchemy import Column, Integer, String
from app.core.database import Base

class TimeTable(Base):
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True)

    
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    branch = Column(String(10), nullable=False)

    
    section = Column(String(10), nullable=True)

    
    faculty_email = Column(String(100), nullable=True)

    
    image_path = Column(String(255), nullable=False)

    uploaded_by = Column(String(100), nullable=False)
