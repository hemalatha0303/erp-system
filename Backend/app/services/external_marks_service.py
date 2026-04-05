from sqlalchemy.orm import Session

from app.models.academic import Academic
from app.models.course_grade import CourseGrade, SemesterGrade
from app.models.external_marks import ExternalMarks
from app.models.student import Student
from app.utils.marks_calculator import calc_cgpa


def _serialize_external_row(em: ExternalMarks) -> dict:
    return {
        "subject_code": em.subject_code,
        "subject_name": em.subject_name,
        "credits": em.credits,
        "external_marks": em.external_marks,
        "grade": em.grade,
    }


def get_semester_result(year: int, semester: int, db: Session, user_email: str) -> dict:
    """
    Legacy path: /student/external-marks/{year}/{semester}
    `year` is ignored; results are keyed by student + semester (and batch when available).

    Populates the same shape the student portal expects: external_marks list,
    semester_results (SGPA/status), and CGPA from semester_grades.
    """
    _ = year  # kept for URL backward compatibility

    student = (
        db.query(Student).filter(Student.user_email == user_email).first()
    )
    if not student:
        return {
            "external_marks": [],
            "semester_results": [],
            "cgpa": 0.0,
        }

    ac = (
        db.query(Academic)
        .filter(Academic.sid == student.id)
        .order_by(Academic.semester.desc())
        .first()
    )
    academic_batch = ac.batch if ac else None

    base_ext = db.query(ExternalMarks).filter(
        ExternalMarks.sid == student.id,
        ExternalMarks.semester == semester,
    )
    external_rows = base_ext.all()
    if academic_batch:
        batched = base_ext.filter(ExternalMarks.batch == academic_batch).all()
        if batched:
            external_rows = batched

    if not external_rows:
        base_cg = db.query(CourseGrade).filter(
            CourseGrade.sid == student.id,
            CourseGrade.semester == semester,
        )
        course_rows = base_cg.all()
        if academic_batch:
            batched_cg = base_cg.filter(CourseGrade.batch == academic_batch).all()
            if batched_cg:
                course_rows = batched_cg
        external_payload = [
            {
                "subject_code": cg.subject_code,
                "subject_name": cg.subject_name,
                "credits": cg.credits,
                "external_marks": cg.external_marks,
                "grade": cg.grade_letter,
            }
            for cg in course_rows
        ]
    else:
        external_payload = [_serialize_external_row(em) for em in external_rows]

    base_sg = db.query(SemesterGrade).filter(
        SemesterGrade.sid == student.id,
        SemesterGrade.semester == semester,
    )
    sem_grade = base_sg.first()
    if academic_batch:
        sg_batched = base_sg.filter(SemesterGrade.batch == academic_batch).first()
        if sg_batched:
            sem_grade = sg_batched

    semester_results = []
    if sem_grade:
        semester_results.append(
            {
                "sgpa": sem_grade.sgpa,
                "cgpa": sem_grade.cgpa,
                "result_status": sem_grade.result_status,
                "total_credits": sem_grade.total_credits,
            }
        )

    all_sem = (
        db.query(SemesterGrade)
        .filter(SemesterGrade.sid == student.id)
        .order_by(SemesterGrade.semester)
        .all()
    )
    cgpa_val = calc_cgpa(all_sem) if all_sem else 0.0
    if sem_grade and sem_grade.cgpa is not None:
        cgpa_val = float(sem_grade.cgpa)

    return {
        "external_marks": external_payload,
        "semester_results": semester_results,
        "cgpa": cgpa_val,
    }
