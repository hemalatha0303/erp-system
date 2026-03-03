
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("STUDENT", "FACULTY", "HOD", "ADMIN"))
    is_active = Column(Boolean, default=True)
