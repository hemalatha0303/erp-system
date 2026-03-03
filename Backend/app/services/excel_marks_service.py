from openpyxl import load_workbook
from io import BytesIO
from decimal import Decimal
from datetime import date

from app.models.internal_marks import InternalMarks
from app.models.external_marks import ExternalMarks
from app.models.student import Student
from app.models.semester_result import SemesterResult
from app.models.subject import Subject
from app.models.academic import Academic

def upload_internal_marks_excel(
    db,
    file,
    year: int,
    semester: int,
    subject_code: str,
    faculty_email: str
):
    file.file.seek(0)
    wb = load_workbook(BytesIO(file.file.read()))
    sheet = wb.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        (
            roll_no,
            subject_code,
            subject_name,
            openbook1,
            openbook2,
            descriptive1,
            descriptive2,
            seminar1,
            seminar2,
            objective1,
            objective2
        ) = row

        student = db.query(Student).filter(
            Student.roll_no == str(roll_no)
        ).first()
        if not student:
            continue

        record = db.query(InternalMarks).filter(
            InternalMarks.sid == student.id,
            InternalMarks.subject_code == subject_code,
            InternalMarks.year == year,
            InternalMarks.semester == semester
        ).first()

        if record:
            record.subject_name = subject_name
            record.openbook1 = openbook1
            record.openbook2 = openbook2
            record.descriptive1 = descriptive1
            record.descriptive2 = descriptive2
            record.seminar1 = seminar1
            record.seminar2 = seminar2
            record.objective1 = objective1
            record.objective2 = objective2
        else:
            db.add(InternalMarks(
                sid=student.id,
                srno=student.roll_no,
                subject_code=subject_code,
                subject_name=subject_name,
                year=year,
                semester=semester,
                openbook1=openbook1,
                openbook2=openbook2,
                descriptive1=descriptive1,
                descriptive2=descriptive2,
                seminar1=seminar1,
                seminar2=seminar2,
                objective1=objective1,
                objective2=objective2,
                entered_by=faculty_email
            ))

    db.commit()
def upload_external_marks_excel(db, file, batch: str, semester: int, admin_email: str):

    file.file.seek(0)
    wb = load_workbook(BytesIO(file.file.read()))
    sheet = wb.active

    processed_students = set()
    for row in sheet.iter_rows(min_row=2, values_only=True):
        roll_no, subject_code, subject_name, grade, gpa, credits = row

        student = db.query(Student).filter(
            Student.roll_no == str(roll_no)
        ).first()
        if not student:
            continue

        academic = db.query(Academic).filter(
            Academic.sid == student.id,
            Academic.batch == batch
        ).first()
        if not academic:
            continue

        db.add(ExternalMarks(
            sid=student.id,
            srno=student.roll_no,
            subject_code=subject_code,
            subject_name=subject_name,
            year=academic.year,
            semester=semester,
            grade=grade,
            gpa=Decimal(str(gpa)),
            credits=credits,
            entered_by=admin_email
        ))

        processed_students.add(student.id)

    
    db.commit()

    for student_id in processed_students:
        calculate_sgpa_and_promote(db, student_id, semester)

    db.commit()
def calculate_sgpa_and_promote(db, student_id: int, semester: int):

    externals = db.query(ExternalMarks).filter(
        ExternalMarks.sid == student_id,
        ExternalMarks.semester == semester
    ).all()

    if not externals:
        return

    total_points = sum(
        Decimal(str(e.gpa)) * Decimal(str(e.credits)) for e in externals
    )
    total_credits = sum(e.credits for e in externals)

    sgpa = round(float(total_points / Decimal(total_credits)), 2)

    academic = db.query(Academic).filter(
        Academic.sid == student_id
    ).first()

    
    exists = db.query(SemesterResult).filter(
        SemesterResult.sid == student_id,
        SemesterResult.semester == semester
    ).first()

    if not exists:
        db.add(SemesterResult(
            sid=student_id,
            srno=academic.srno,
            year=academic.year,
            semester=semester,
            sgpa=sgpa,
            total_credits=total_credits,
            result_status="PASS"
        ))

    promote_student_after_external(db, academic)
def promote_student_after_external(db, academic: Academic):

    academic.semester += 1
    if academic.semester in (3, 5, 7):
        academic.year += 1
