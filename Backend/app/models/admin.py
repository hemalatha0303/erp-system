
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    mobile_no = Column(String(15))
    designation = Column(String(50))
