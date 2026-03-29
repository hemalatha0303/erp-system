from app.models import user
from app.models.academic import Academic
from app.models.external_marks import ExternalMarks
from app.models.semester_result import SemesterResult
from app.models.student import Student
from app.utils.marks_calculator import calc_cgpa


def get_semester_result(year: int, semester: int, db, user_email):
    student = db.query(Student).filter(
        Student.user_email == user_email
    ).first()   
    externalmarks = db.query(ExternalMarks).filter(
        ExternalMarks.rollno == student.roll_no,
        ExternalMarks.year == year,
        ExternalMarks.semester == semester
    ).all()
    result = db.query(SemesterResult).filter(
        SemesterResult.rollno == student.roll_no,
        SemesterResult.year == year,
        SemesterResult.semester == semester
    ).all()
    all_results = db.query(SemesterResult).filter(
        SemesterResult.rollno == student.roll_no
    ).all()
    cgpa = calc_cgpa(all_results)
    return {
        "external_marks": externalmarks,
        "semester_results": result,
        "cgpa": cgpa
    }
