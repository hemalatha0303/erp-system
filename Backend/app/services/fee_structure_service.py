from sqlalchemy.orm import Session
from app.models.fee_structure import FeeStructure

def bulk_create_fee_structure(db: Session, items: list):
    for data in items:
        exists = db.query(FeeStructure).filter(
            FeeStructure.quota == data["quota"],
            FeeStructure.residence_type == data["residence_type"],
            FeeStructure.year == data["year"],
            
        ).first()

        if not exists:
            db.add(FeeStructure(**data))

    db.commit()
    return "Bulk fee structure inserted"

def create_fee_structure(db: Session, data: dict):
    existing = db.query(FeeStructure).filter(
        FeeStructure.quota == data["quota"],
        FeeStructure.residence_type == data["residence_type"],
        FeeStructure.year == data["year"],
        
    ).first()

    if existing:
        return False, "Fee structure already exists"

    fee = FeeStructure(
        quota=data["quota"],
        residence_type=data["residence_type"],
        tuition_fee=data["tuition_fee"],
        bus_fee=data["bus_fee"],
        hostel_fee=data["hostel_fee"],
        year=data["year"],
        
    )

    db.add(fee)
    db.commit()
    return True, "Fee structure added successfully"
