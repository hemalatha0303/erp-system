from sqlalchemy import Column, Integer, String, DECIMAL
from app.core.database import Base

class FeeStructure(Base):
    __tablename__ = "fee_structure"

    id = Column(Integer, primary_key=True)
    quota = Column(String(20))                 
    residence_type = Column(String(20))        

    tuition_fee = Column(DECIMAL(10,2))
    bus_fee = Column(DECIMAL(10,2))
    hostel_fee = Column(DECIMAL(10,2))

    year = Column(Integer)
    
