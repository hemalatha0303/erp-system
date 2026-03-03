from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.core.database import Base
class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("students.id"))
    room_id = Column(Integer, ForeignKey("hostel_rooms.id"))

    allocated_date = Column(Date)
    vacated_date = Column(Date, nullable=True)

    status = Column(String(20))  

    allocated_by = Column(String(100))
