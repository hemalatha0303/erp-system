
from app.models.academic import Academic
from app.models.hostel_room import HostelRoom

from app.models.hostel_allocation import HostelAllocation
from app.models.student import Student
from datetime import date
from app.models.payment import Payment
from app.models.fee_structure import FeeStructure
from openpyxl import load_workbook
from io import BytesIO
from app.models.hostel_room import HostelRoom

def upload_hostel_rooms_excel(db, file):

    file.file.seek(0)
    wb = load_workbook(BytesIO(file.file.read()))
    sheet = wb.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        room_number, sharing, room_type, capacity = row

        if not room_number:
            continue

        
        exists = db.query(HostelRoom).filter(
            HostelRoom.room_number == str(room_number)
        ).first()

        if exists:
            continue

        room = HostelRoom(
            room_number=str(room_number),
            sharing=int(sharing),
            room_type=str(room_type).upper(),
            capacity=int(capacity),
            occupied=0,
            is_active=True
        )
        db.add(room)

    db.commit()

def allocate_student_hostel(db, req, admin_email):

    student = db.query(Student).filter(
        Student.roll_no == req.roll_no
    ).first()

    if student.residence_type != "HOSTELER":
        raise Exception("Student is not a hosteler")

    room = db.query(HostelRoom).filter(
        HostelRoom.room_number == req.room_number,
        HostelRoom.is_active == True
    ).first()

    if room.occupied >= room.capacity:
        raise Exception("Room is full")

    existing = db.query(HostelAllocation).filter(
        HostelAllocation.student_id == student.id,
        HostelAllocation.status == "ALLOCATED"
    ).first()

    if existing:
        raise Exception("Student already allocated")

    allocation = HostelAllocation(
        student_id=student.id,
        room_id=room.id,
        allocated_date=date.today(),
        status="ALLOCATED",
        allocated_by=admin_email
    )

    room.occupied += 1

    db.add(allocation)
    db.commit()
def get_student_hostel_details(db, student_email):

    student = db.query(Student).filter(
        Student.user_email == student_email
    ).first()
    academic = db.query(Academic).filter(
        Academic.sid == student.id
    ).first()
    allocation = (
        db.query(HostelAllocation, HostelRoom)
        .join(HostelRoom, HostelRoom.id == HostelAllocation.room_id)
        .filter(
            HostelAllocation.student_id == student.id,
            HostelAllocation.status == "ALLOCATED"
        )
        .first()
    )

    fee_struct = db.query(FeeStructure).filter(
        FeeStructure.quota == academic.quota,
        FeeStructure.residence_type == "HOSTELER",
        FeeStructure.year == academic.year
    ).first()
    payment = db.query(Payment).filter(
        Payment.srno == student.roll_no,  
        Payment.year == academic.year,
        Payment.fee_type == "HOSTEL"
    ).first()
    if not allocation:
        return {"hostel": None}
    if not fee_struct :
        return {"hostel": None}
    if payment.amount_paid is None:
        payment.amount_paid = 0
    alloc, room = allocation

    return {
        "room_number": room.room_number,
        "room_type": room.room_type,
        "sharing": room.sharing,
        "allocated_date": alloc.allocated_date,
        "fee": {
            "total": float(fee_struct.hostel_fee),
            "paid": float(payment.amount_paid),
            "due": float(fee_struct.hostel_fee - payment.amount_paid),
            "status": payment.status,
            "last_paid_date": payment.payment_date
        }
    }

def vacate_hostel_room(db, req, admin_email):

    student = db.query(Student).filter(
        Student.roll_no == req.roll_no
    ).first()
    allocation = db.query(HostelAllocation).filter(
        HostelAllocation.student_id == student.id,
        HostelAllocation.status == "ALLOCATED"
    ).first()
    if not allocation:
        raise Exception("No active allocation found for the student")
    
    room = db.query(HostelRoom).filter(
        HostelRoom.room_number == req.room_number
    ).first()
    allocation.status = "VACATED"
    allocation.vacated_date = date.today()
    room.occupied -= 1
    db.commit()
