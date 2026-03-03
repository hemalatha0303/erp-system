from sqlalchemy import Column, Date, Integer, String, ForeignKey
from app.core.database import Base
from datetime import date
class HODProfile(Base):
    __tablename__ = "hod"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    department = Column(String(50))
    mobile_no = Column(String(15))
    qualification = Column(String(100))
    experience = Column(Integer)
    join_date = Column(Date, default=date.today)