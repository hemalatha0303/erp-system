from sqlalchemy.orm import Session
from app.models.academic import Academic
from app.models.student import Student

def create_academics_bulk(db: Session, rows: list):
    for r in rows:
        student = db.query(Student).filter(Student.roll_no == r["srno"]).first()

        academic = Academic(
            sid=student.id if student else None,
            user_email=student.user_email if student else None,
            srno=r["srno"],
            branch=r["branch"],
            batch=r["batch"],
            course=r["course"],
            year=r["year"],
            semester=r["semester"],
            section=r["section"],
            type=r["type"],
            admission_date=r["admission_date"],
            status=r["status"]
        )
        db.add(academic)
    db.commit()


def insert_academics_bulk(db: Session, rows: list):
    for row in rows:
        
        student = db.query(Student).filter(
            Student.roll_no == row["srno"]
        ).first()

        if not student:
            continue

        academic = Academic(
            sid=student.id,              
            user_email=student.user_email,
            srno=row["srno"],
            branch=row["branch"],
            batch=row["batch"],
            course=row["course"],
            year=row["year"],
            semester=row["semester"],
            section=row["section"],
            type=row["type"],
            quota=row.get("quota"),
            admission_date=row["admission_date"],
            status=row["status"]
        )

        db.add(academic)

    db.commit()
