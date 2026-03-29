from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.academic import Academic
from app.models.student import Student
from app.models.fee_structure import FeeStructure
from app.models.payment import Payment


def get_fee_compliance_summary(db: Session, batch: str, year: int):
    records = db.query(
        Academic.srno,
        Academic.quota,
        Student.residence_type
    ).join(
        Student, Student.roll_no == Academic.srno
    ).filter(
        Academic.batch == batch
    ).all()

    fully_paid = partially_paid = not_paid = 0

    for r in records:
        
        fee = db.query(FeeStructure).filter(
            FeeStructure.year == year,
            FeeStructure.quota == r.quota,
            FeeStructure.residence_type == r.residence_type
        ).first()

        total_fee = (
            (fee.tuition_fee or 0) +
            (fee.bus_fee or 0) +
            (fee.hostel_fee or 0)
        ) if fee else 0

        
        paid = db.query(func.coalesce(func.sum(Payment.amount_paid), 0))\
            .filter(
                Payment.srno == r.srno,
                Payment.year == year
            ).scalar()

        if paid == 0:
            not_paid += 1
        elif paid < total_fee:
            partially_paid += 1
        else:
            fully_paid += 1

    return {
        "fully_paid": fully_paid,
        "partially_paid": partially_paid,
        "not_paid": not_paid
    }