from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base
class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    id = Column(Integer, primary_key=True)

    room_number = Column(String(10), unique=True, nullable=False)
    sharing = Column(Integer)          
    room_type = Column(String(10))     
    capacity = Column(Integer)         
    occupied = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
