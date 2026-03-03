from datetime import date
from decimal import Decimal
from collections import defaultdict

from app.models.student import Student
from app.models.academic import Academic
from app.models.payment import Payment
from app.models.fee_structure import FeeStructure


def format_fee_type(fee_type: str) -> str:
    return {
        "TUITION": "Tuition Fees",
        "HOSTEL": "Hostel Fees",
        "BUS": "Bus/Transport Fees",
    }.get(fee_type, fee_type)


def get_payment_details_by_roll(db, roll_no: str):

    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    if not student:
        return None

    academic = db.query(Academic).filter(Academic.sid == student.id).first()

    fees = (
        db.query(FeeStructure)
        .filter(
            FeeStructure.quota == academic.quota,
            FeeStructure.residence_type == student.residence_type,
            FeeStructure.year == academic.year,
        )
        .first()
    )

    payments = {
        p.fee_type: p
        for p in db.query(Payment)
        .filter(Payment.srno == roll_no, Payment.year == academic.year)
        .all()
    }

    fee_map = {
        "TUITION": fees.tuition_fee,
        "BUS": fees.bus_fee,
        "HOSTEL": fees.hostel_fee,
    }

    result = []
    for fee_type, total in fee_map.items():
        paid = (
            payments.get(fee_type).amount_paid
            if fee_type in payments
            else Decimal("0.0")
        )

        result.append(
            {
                "fee_type": fee_type,
                "total_fee": float(total),
                "paid": float(paid),
                "balance": float(total - paid),
            }
        )

    return {
        "roll_no": roll_no,
        "name": f"{student.first_name} {student.last_name}",
        "year": academic.year,
        "fees": result,
    }


def update_student_payment(db, req, admin_email):

    academic = (
        db.query(Academic)
        .filter(Academic.srno == req.roll_no)
        .order_by(Academic.year.desc())
        .first()
    )

    if not academic:
        raise Exception("Academic record not found")

    student = db.query(Student).filter(Student.roll_no == req.roll_no).first()

    fees = (
        db.query(FeeStructure)
        .filter(
            FeeStructure.quota == academic.quota,
            FeeStructure.residence_type == student.residence_type,
            FeeStructure.year == academic.year,
        )
        .first()
    )

    fee_type = req.fee_type.upper().strip()
    if fee_type == "TUTION":
        fee_type = "TUITION"

    payment = (
        db.query(Payment)
        .filter(
            Payment.srno == req.roll_no,
            Payment.fee_type == fee_type,
            Payment.year == academic.year,
        )
        .first()
    )

    if not payment:
        raise Exception(f"Payment record not found for {fee_type}")

    payment.amount_paid = Decimal(payment.amount_paid) + Decimal(str(req.amount))
    payment.payment_mode = req.payment_mode
    payment.payment_date = date.today()
    payment.updated_by = admin_email

    total_fee = {
        "TUITION": fees.tuition_fee,
        "BUS": fees.bus_fee,
        "HOSTEL": fees.hostel_fee,
    }[fee_type]

    payment.status = "PAID" if payment.amount_paid >= total_fee else "PENDING"

    db.commit()


def get_student_payment_details(db, student_email: str, semester: int):

    student = db.query(Student).filter(Student.user_email == student_email).first()
    year = (semester + 1) // 2 
    sem = 1 if semester % 2 != 0 else 2
    print(year, sem)

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
        return {"semester": semester, "structure": [], "transactions": []}

    fees = (
        db.query(FeeStructure)
        .filter(
            FeeStructure.quota == academic.quota,
            FeeStructure.residence_type == student.residence_type,
            FeeStructure.year == academic.year,
        )
        .first()
    )

    payments = (
        db.query(Payment)
        .filter(Payment.student_email == student_email,Payment.year == year)
        .order_by(Payment.payment_date)
        .all()
    )
    print(payments  )
    structure = []
    transactions = []

    fee_map = {
        "TUITION": fees.tuition_fee,
        "HOSTEL": fees.hostel_fee,
        "BUS": fees.bus_fee,
    }

    paid_map = defaultdict(Decimal)

    for p in payments:
        paid_map[p.fee_type] += p.amount_paid

        if p.amount_paid > 0:
            transactions.append(
                {
                    "date": p.payment_date.strftime("%d-%b-%Y"),
                    "type": format_fee_type(p.fee_type),
                    "ref": p.receipt_id,
                    "amount": float(p.amount_paid),
                    "remBalance": float(fee_map[p.fee_type] - paid_map[p.fee_type]),
                }
            )

    for fee_type, total in fee_map.items():
        paid = paid_map[fee_type]
        structure.append(
            {
                "type": format_fee_type(fee_type),
                "total": float(total),
                "paid": float(paid),
                "balance": float(total - paid),
                "status": "Paid" if paid >= total else "Partial",
            }
        )

    return {"semester": semester, "structure": structure, "transactions": transactions}