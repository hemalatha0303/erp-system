from sqlalchemy.orm import Session
from app.models import payment
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.academic import Academic

def get_faculty_by_email(db: Session, email: str):
    return db.query(Faculty).filter(Faculty.user_email == email).first()

def upsert_faculty_profile(db: Session, email: str, data):
    faculty = get_faculty_by_email(db, email)
    if not faculty:
        faculty = Faculty(user_email=email)

    faculty.first_name = data.first_name
    faculty.last_name = data.last_name
    faculty.mobile_no = data.mobile_no
    faculty.address = data.address
    faculty.qualification = data.qualification
    faculty.experience = data.experience
    if getattr(data, "personal_email", None) is not None:
        faculty.personal_email = data.personal_email
    if getattr(data, "subject_code", None) is not None:
        faculty.subject_code = data.subject_code
    if getattr(data, "subject_name", None) is not None:
        faculty.subject_name = data.subject_name
    if getattr(data, "branch", None) is not None:
        faculty.branch = data.branch

    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty

def get_student_info_by_rollno(db: Session, roll_no: str):
    student = db.query(Student).filter(
        Student.roll_no == roll_no
    ).first()

    if not student:
        return None

    academic = db.query(Academic).filter(
        Academic.sid == student.id
    ).order_by(Academic.year.desc()).first()
    
    payment_records = db.query(payment.Payment).filter(
        payment.Payment.srno == student.roll_no
    ).all()
    
    # Serialize payment records properly
    payment_data = []
    for p in payment_records:
        amount_val = getattr(p, "amount", None)
        payment_data.append({
            "fee_type": p.fee_type,
            "amount": amount_val,
            "amount_paid": p.amount_paid,
            "balance": (amount_val or 0) - (p.amount_paid or 0),
            "status": p.status,
            "due_date": str(getattr(p, "due_date", None)) if getattr(p, "due_date", None) else None
        })
    
    return {
        "roll_no": student.roll_no,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.user_email,
        "mobile_no": student.mobile_no,
        "parent_mobile_no": student.parent_mobile_no,
        "address": student.address,
        "parentname": student.parentname,
        "branch": academic.branch if academic else None,
        "batch": academic.batch if academic else None,
        "course": academic.course if academic else None,
        "year": academic.year if academic else None,
        "semester": academic.semester if academic else None,
        "section": academic.section if academic else None,
        "type": academic.type if academic else None,
        "status": academic.status if academic else None,
        "payment_records": payment_data
    }
