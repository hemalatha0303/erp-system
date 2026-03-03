from decimal import Decimal
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
from app.models.student import Student
from collections import defaultdict
from calendar import month_name
from app.models.attendance_session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
from sqlalchemy import extract
from sqlalchemy import func, case


def mark_attendance(db, req, faculty_email):

    
    exists = db.query(AttendanceSession).filter(
        AttendanceSession.subject_code == req.subject_code,
        AttendanceSession.date == req.date,
        AttendanceSession.period == req.period,
        AttendanceSession.semester == req.semester
    ).first()

    if exists:
        raise Exception("Attendance already marked for this subject & period")

    session = AttendanceSession(
        subject_code=req.subject_code,
        subject_name=req.subject_name,
        year=req.year,
        semester=req.semester,
        date=req.date,
        period=req.period,
        faculty_email=faculty_email
    )

    db.add(session)
    db.flush()  

    for item in req.attendance:
        student = db.query(Student).filter(
            Student.roll_no == item.roll_no
        ).first()
        if not student:
            continue

        db.add(AttendanceRecord(
            session_id=session.id,
            sid=student.id,
            srno=student.roll_no,
            status=item.status.upper()
        ))

    db.commit()


def get_student_attendance(db, student_id, subject_code):

    total = db.query(AttendanceRecord).join(
        AttendanceSession
    ).filter(
        AttendanceRecord.sid == student_id,
        AttendanceSession.subject_code == subject_code
    ).count()

    present = db.query(AttendanceRecord).join(
        AttendanceSession
    ).filter(
        AttendanceRecord.sid == student_id,
        AttendanceSession.subject_code == subject_code,
        AttendanceRecord.status == "PRESENT"
    ).count()

    percentage = round((present / total) * 100, 2) if total else 0

    return {
        "subject_code": subject_code,
        "total_periods": total,
        "present_periods": present,
        "percentage": percentage
    }
def get_student_monthly_attendance(db, student_id: int, month: int, year: int):

    records = (
        db.query(
            AttendanceSession.date,
            AttendanceSession.subject_name,
            AttendanceSession.subject_code,
            AttendanceSession.period,
            AttendanceRecord.status
        )
        .join(
            AttendanceRecord,
            AttendanceSession.id == AttendanceRecord.session_id
        )
        .filter(
            AttendanceRecord.sid == student_id,
            extract("month", AttendanceSession.date) == month,
            extract("year", AttendanceSession.date) == year
        )
        .order_by(
            AttendanceSession.date,
            AttendanceSession.period
        )
        .all()
    )

    attendance_map = defaultdict(list)
    summary = defaultdict(lambda: {"total": 0, "present": 0})
    for r in records:
        attendance_map[str(r.date)].append({
            "subject": r.subject_name,
            "subject_code": r.subject_code,
            "period": r.period,
            "status": r.status
        })
        summary[r.subject_name]["total"] += 1
        if r.status == "PRESENT":
            summary[r.subject_name]["present"] += 1
    subject_summary = []
    for subject, data in summary.items():
        percentage = round(
            (data["present"] / data["total"]) * 100, 2
        )
        subject_summary.append({
            "subject": subject,
            "total_classes": data["total"],
            "attended": data["present"],
            "percentage": percentage
        })

    return {
        "month": month_name[month],
        "year": year,
        "attendance": attendance_map,
        "subject_summary": subject_summary
    }
def get_semester_attendance_summary(db, srno: str, semester: int):

    result = (
        db.query(
            func.count(AttendanceRecord.id).label("total_classes"),
            func.coalesce(
                func.sum(
                    case(
                        (func.upper(AttendanceRecord.status) == "PRESENT", 1),
                        else_=0
                    )
                ),
                0
            ).label("attended_classes")
        )
        .join(
            AttendanceSession,
            AttendanceRecord.session_id == AttendanceSession.id
        )
        .filter(
            AttendanceRecord.srno == srno,
            AttendanceSession.semester == semester
        )
        .first()
    )

    total = result.total_classes
    attended = result.attended_classes

    percentage = round((attended / total) * 100, 2) if total else 0

    return {
        "total_classes": total,
        "attended_classes": attended,
        "absent_classes": total - attended,
        "attendance_percentage": percentage,
        "eligible_for_exam": percentage >= 75
    }
def get_subject_wise_attendance(db, srno: str, semester: int):

    rows = (
        db.query(
            AttendanceSession.subject_code,
            AttendanceSession.subject_name,
            func.count(AttendanceRecord.id).label("total_classes"),
            func.coalesce(
                func.sum(
                    case(
                        (func.upper(AttendanceRecord.status) == "PRESENT", 1),
                        else_=0
                    )
                ),
                0
            ).label("attended_classes")
        )
        .join(
            AttendanceSession,
            AttendanceRecord.session_id == AttendanceSession.id
        )
        .filter(
            AttendanceRecord.srno == srno,
            AttendanceSession.semester == semester
        )
        .group_by(
            AttendanceSession.subject_code,
            AttendanceSession.subject_name
        )
        .all()
    )

    response = []
    for r in rows:
        percentage = round(
            (r.attended_classes / r.total_classes) * 100, 2
        ) if r.total_classes else 0

        response.append({
            "subject_code": r.subject_code,
            "subject_name": r.subject_name,
            "total_classes": r.total_classes,
            "attended_classes": r.attended_classes,
            "attendance_percentage": percentage
        })

    return response
def get_low_subjects(db, srno: str, semester: int, threshold: float = 75.0):
    
    rows = get_subject_wise_attendance(db, srno, semester)

    low_subjects = []
    threshold = Decimal("75.0")
    
    for r in rows:
        total = r["total_classes"]
        attended = r["attended_classes"]

        percentage = round((attended / total) * 100, 2) if total else 0
        percentage = Decimal(percentage)
        if percentage < threshold:
            low_subjects.append({
                "subject_code": r["subject_code"],
                "subject_name": r["subject_name"],
                "total_classes": total,
                "attended_classes": attended,
                "attendance_percentage": percentage,
                "required_percentage": threshold,
                "short_by": round(threshold - percentage, 2)
            })

    return low_subjects