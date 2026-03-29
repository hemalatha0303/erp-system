from sqlalchemy.orm import Session
from app.models.student import Student

def get_student_by_email(db: Session, email: str):
    return db.query(Student).filter(Student.user_email == email).first()

def upsert_student_profile(db: Session, email: str, data):
    student = get_student_by_email(db, email)

    if not student:
        
        student = Student(user_email=email)

    
    student.roll_no = data.roll_no
    student.first_name = data.first_name
    student.last_name = data.last_name
    student.gender = data.gender
    student.blood_group = data.blood_group
    student.date_of_birth = data.date_of_birth
    student.mobile_no = data.mobile_no
    student.parent_mobile_no = data.parent_mobile_no
    student.address = data.address
    student.parentname = data.parentname
    db.add(student)
    db.commit()
    db.refresh(student)

    return student
