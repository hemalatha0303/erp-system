from app.models import user
from app.models.academic import Academic
from app.models.external_marks import ExternalMarks
from app.models.semester_result import SemesterResult
from app.models.student import Student


def get_semester_result(year: int, semester: int, db, user_email):
    student = db.query(Student).filter(
        Student.user_email == user_email
    ).first()   
    externalmarks = db.query(ExternalMarks).filter(
        ExternalMarks.srno == student.roll_no,
        ExternalMarks.year == year,
        ExternalMarks.semester == semester
    ).all()
    result = db.query(SemesterResult).filter(
        SemesterResult.srno == student.roll_no,
        SemesterResult.year == year,
        SemesterResult.semester == semester
    ).all()
    return {
        "external_marks": externalmarks,
        "semester_results": result
    }