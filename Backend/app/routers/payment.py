from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.payment_service import get_payment_details_by_roll, update_student_payment
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.payment import PaymentUpdateRequest
from app.models.student import Student
from app.models.academic import Academic
from app.models.fee_structure import FeeStructure
from app.models.payment import Payment
from collections import defaultdict
from decimal import Decimal
def format_fee_type(fee_type: str) -> str:
    return {
        "TUITION": "Tuition Fees",
        "HOSTEL": "Hostel Fees",
        "BUS": "Bus/Transport Fees",
    }.get(fee_type, fee_type)

router = APIRouter(prefix="/payments")

@router.get("/my")
def my_payments(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)

    return get_payment_details_by_roll(db, user["sub"])
@router.get("/payment/{roll_no}")
def get_student_payment_info(
    roll_no: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admin allowed")

    # 1. Fetch the "normal" payment details (Profile info, current semester data)
    data = get_payment_details_by_roll(db, roll_no)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")

    # 2. Fetch Student for the history query
    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    all_payments = (
        db.query(Payment)
        .filter(Payment.srno == student.roll_no)
        .order_by(Payment.payment_date.desc())
        .all()
    )

    transactions = []
    paid_map_by_year = defaultdict(lambda: defaultdict(Decimal))

    for p in all_payments:
        paid_map_by_year[p.year][p.fee_type] += p.amount_paid

        if p.amount_paid > 0:
            transactions.append(
                {
                    "date": p.payment_date.strftime("%d-%b-%Y") if p.payment_date else "N/A",
                    "type": format_fee_type(p.fee_type),
                    "ref": p.receipt_id,
                    "amount": float(p.amount_paid),
                    "year_paid_for": p.year, 
                }
            )

    all_semesters_data = []


    for current_sem in range(1, 9):
        year = (current_sem + 1) // 2 
        sem = 1 if current_sem % 2 != 0 else 2

        academic = (
            db.query(Academic)
            .filter(
                Academic.sid == student.id,
                Academic.year == year,
                Academic.semester == sem
            )
            .first()
        )

        if not academic:
            continue

        fees = (
            db.query(FeeStructure)
            .filter(
                FeeStructure.quota == academic.quota,
                FeeStructure.residence_type == student.residence_type,
                FeeStructure.year == academic.year,
            )
            .first()
        )

        if not fees:
            continue

        fee_map = {
            "TUITION": fees.tuition_fee,
            "HOSTEL": fees.hostel_fee,
            "BUS": fees.bus_fee,
        }

        structure = []
        paid_map = paid_map_by_year[year]

        for fee_type, total in fee_map.items():
            if total > 0: 
                paid = paid_map[fee_type]
                
                if paid >= total:
                    status = "Paid"
                elif paid > 0:
                    status = "Partial"
                else:
                    status = "Unpaid"

                structure.append(
                    {
                        "type": format_fee_type(fee_type),
                        "total": float(total),
                        "paid": float(paid),
                        "balance": float(total - paid),
                        "status": status,
                    }
                )

        all_semesters_data.append({
            "semester": current_sem,
            "year": year,
            "structure": structure
        })

    data["transactions"] = transactions 
    data["all_semesters"] = all_semesters_data

    return data
@router.post("/payment/update")
def update_payment(
    req: PaymentUpdateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    update_student_payment(db, req, user["sub"])
    return {"message": "Payment updated successfully"}
