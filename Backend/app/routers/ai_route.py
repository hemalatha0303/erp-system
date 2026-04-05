from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.student import Student
from app.models.academic import Academic
from app.models.internal_marks import InternalMarks
from app.models.external_marks import ExternalMarks
from app.models.course_grade import SemesterGrade
from app.services.attendance_service import get_low_subjects
from app.services.ai_service import get_attendance_advice
from app.services.attendance_service import get_semester_attendance_summary
from app.services.inference import predict_student_risk_structured

router = APIRouter(prefix="/ai", tags=["AI Services"])

MID_CAP = 30.0


def _clamp_mid_component(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(MID_CAP, v))


def _internal_mark_features(internals: list):
    """
    Mid exams are out of 30. Clamp stored values to handle bad data.
    Returns avg_mid1, avg_mid2 (for the ML model) and mid_score_average (for UI, out of 30).
    """
    if not internals:
        return 0.0, 0.0, 0.0

    m1_list = []
    m2_list = []
    final_list = []
    combined_per_subject = []

    for row in internals:
        m1 = _clamp_mid_component(row.mid1)
        m2 = _clamp_mid_component(row.mid2)
        m1_list.append(m1)
        m2_list.append(m2)
        if row.final_internal_marks is not None:
            final_list.append(_clamp_mid_component(row.final_internal_marks))
        combined_per_subject.append((m1 + m2) / 2.0)

    avg_mid1 = sum(m1_list) / len(m1_list)
    avg_mid2 = sum(m2_list) / len(m2_list)

    if final_list:
        mid_avg = sum(final_list) / len(final_list)
    else:
        mid_avg = sum(combined_per_subject) / len(combined_per_subject)

    return avg_mid1, avg_mid2, min(MID_CAP, mid_avg)


@router.get("/student/attendance/ai-advice")
def attendance_ai_advice(
    semester: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()

    if not student:
        return {"message": "Student not found"}

    low_attendance = get_low_subjects(
        db=db,
        srno=student.roll_no,
        semester=semester,
    )

    if not low_attendance:
        return {
            "message": "🎉 Your attendance is good in all subjects!",
            "eligible_for_exam": True,
        }

    ai_message = get_attendance_advice(low_attendance)

    return {
        "eligible_for_exam": False,
        "low_attendance": low_attendance,
        "ai_message": ai_message,
    }


@router.get("/aews/student-risk/{roll_no}")
def faculty_student_risk(
    roll_no: str,
    semester: int = 1,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Faculty-facing risk assessment: uses the same feature layout as the student dashboard model.
    """
    if user.get("role") != "FACULTY":
        raise HTTPException(status_code=403, detail="Faculty access only")

    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    if not student:
        return {"status": "error", "detail": "Student not found"}

    att_data = get_semester_attendance_summary(db, student.roll_no, semester)
    att_percentage = float(att_data.get("attendance_percentage") or 0)

    sem_grades = (
        db.query(SemesterGrade)
        .filter(SemesterGrade.sid == student.id)
        .order_by(SemesterGrade.semester)
        .all()
    )
    prev_sgpa = 0.0
    if sem_grades:
        prior = [g for g in sem_grades if g.semester < semester]
        if prior:
            prev_sgpa = float(prior[-1].sgpa or 0)
        else:
            prev_sgpa = float(sem_grades[-1].sgpa or 0)

    backlogs = (
        db.query(ExternalMarks)
        .filter(ExternalMarks.sid == student.id, ExternalMarks.grade == "F")
        .count()
    )

    internals = (
        db.query(InternalMarks)
        .filter(InternalMarks.sid == student.id, InternalMarks.semester == semester)
        .all()
    )

    avg_mid1, avg_mid2, mid_avg = _internal_mark_features(internals)

    student_features = {
        "mid1_exam_30": avg_mid1,
        "mid2_exam_30": avg_mid2,
        "attendance_pct_100": att_percentage,
        "prev_year_sgpa_10": prev_sgpa,
        "backlogs": backlogs,
    }

    structured = predict_student_risk_structured(student_features)

    academic = (
        db.query(Academic)
        .filter(Academic.sid == student.id)
        .order_by(Academic.semester.desc())
        .first()
    )

    return {
        "status": "success",
        "roll_no": student.roll_no,
        "student_name": f"{student.first_name} {student.last_name}".strip(),
        "student_email": (student.user_email or "").strip(),
        "batch": academic.batch if academic else "",
        "branch": academic.branch if academic else "",
        "section": academic.section if academic else "",
        "risk_level": structured["risk_level"],
        "risk_probability": structured["risk_probability"],
        "explanation": structured["explanation"],
        "factors": {
            "attendance": round(att_percentage, 1),
            "backlogs": backlogs,
            "previous_sgpa": round(prev_sgpa, 2),
            "mid_score_average": round(mid_avg, 2),
        },
    }
