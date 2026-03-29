
from sqlalchemy import Column, Integer, String, Date, DECIMAL, Text
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    receipt_id = Column(String(50), unique=True, nullable=False)
    srno = Column(String(20), nullable=False)
    student_email = Column(String(100), nullable=False)

    fee_type = Column(String(20))          
    amount_paid = Column(DECIMAL(10,2))    

    payment_mode = Column(String(30))
    status = Column(String(20))
    description = Column(Text)

    year = Column(Integer)
    semester = Column(Integer)
    payment_date = Column(Date)
    updated_by = Column(String(100))
