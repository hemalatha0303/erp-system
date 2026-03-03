from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.notification_service import get_student_notifications
from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.models.external_marks import ExternalMarks
from app.models.semester_result import SemesterResult
from app.models.student import Student
from app.models.internal_marks import InternalMarks
from app.models.timetable import TimeTable
from app.schemas.student import StudentProfileRequest, StudentProfileResponse
from app.services.library_service import get_student_library_books
from app.services.external_marks_service import get_semester_result
from app.services.hostel_service import get_student_hostel_details
from app.services.student_service import get_student_by_email, upsert_student_profile
from app.services.payment_service import get_student_payment_details
from app.services.internal_marks_service import get_internal_marks_by_student
from app.services.attendance_service import (
    get_semester_attendance_summary,
    get_student_monthly_attendance,
    get_subject_wise_attendance,
)
from app.services.attendance_service import get_low_subjects
from app.services.ai_service import get_attendance_advice
from sqlalchemy import func
from app.models.academic import Academic
from app.models.payment import Payment
from app.models.library_issue import LibraryIssue
from app.models.attendance_record import AttendanceRecord
from app.models.attendance_session import AttendanceSession
from app.services.inference import predict_student_risk 
from app.models.academic import Academic
from app.models.alert import Alert
router = APIRouter(prefix="/student", tags=["Student"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.notification_service import get_student_notifications
from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.models.external_marks import ExternalMarks
from app.models.semester_result import SemesterResult
from app.models.student import Student
from app.models.internal_marks import InternalMarks
from app.models.timetable import TimeTable
from app.schemas.student import StudentProfileRequest, StudentProfileResponse
from app.services.library_service import get_student_library_books
from app.services.hostel_service import get_student_hostel_details
from app.services.student_service import get_student_by_email, upsert_student_profile
from app.services.payment_service import get_student_payment_details
from app.services.attendance_service import get_semester_attendance_summary
# Import the new inference service
from app.services.inference import predict_student_risk 
from app.models.academic import Academic

router = APIRouter(prefix="/student", tags=["Student"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard")
def get_student_dashboard_data(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403, detail="Access denied")

    email = user["sub"]
    
    # 1. Fetch Basic Info
    student = db.query(Student).filter(Student.user_email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    academic = db.query(Academic).filter(Academic.sid == student.id).order_by(Academic.year.desc()).first()
    current_sem = academic.semester if academic else 1

    # 2. Fetch Features for AI Model
    
    # Feature: Attendance %
    att_data = get_semester_attendance_summary(db, student.roll_no, current_sem)
    att_percentage = att_data["attendance_percentage"]

    # Feature: CGPA / Previous SGPA
    results = db.query(SemesterResult).filter(SemesterResult.srno == student.roll_no).all()
    if results:
        total_sgpa = sum([r.sgpa for r in results if r.sgpa is not None])
        cgpa = round(total_sgpa / len(results), 2)
        prev_sgpa = results[-1].sgpa if results[-1].sgpa else cgpa
    else:
        cgpa = 0.0
        prev_sgpa = 0.0

    # Feature: Backlogs (Count of 'F' grades)
    backlogs = db.query(ExternalMarks).filter(
        ExternalMarks.sid == student.id, 
        ExternalMarks.grade == 'F'
    ).count()

    # Feature: Internal Marks (Mid 1 & Mid 2)
    internals = db.query(InternalMarks).filter(
        InternalMarks.sid == student.id,
        InternalMarks.semester == current_sem
    ).all()

    avg_mid1 = 0
    avg_mid2 = 0
    if internals:
        # Sum components (OpenBook+Desc+Sem+Obj = Max 25) and scale to 30 if needed by model
        # Assuming model expects values around 0-30 based on header 'mid1_exam_30'
        m1_totals = [(i.openbook1 + i.descriptive1 + i.seminar1 + i.objective1) for i in internals]
        m2_totals = [(i.openbook2 + i.descriptive2 + i.seminar2 + i.objective2) for i in internals]
        
        # Scale 25 -> 30 (Multiply by 1.2)
        avg_mid1 = (sum(m1_totals) / len(m1_totals)) * 1.2
        avg_mid2 = (sum(m2_totals) / len(m2_totals)) * 1.2

    # 3. Call Local AI Inference
    student_features = {
        "mid1_exam_30": avg_mid1,
        "mid2_exam_30": avg_mid2,
        "attendance_pct_100": att_percentage,
        "prev_year_sgpa_10": prev_sgpa,
        "backlogs": backlogs
    }
    
    ai_msg = predict_student_risk(student_features)

    # 4. Other Dashboard Data
    payment_data = get_student_payment_details(db, email, academic.semester + academic.year)
    total_dues = sum([item["balance"] for item in payment_data["structure"]]) if payment_data else 0

    lib_data = get_student_library_books(db, email, current_sem)
    active_books_count = len(lib_data["books"])

    return {
        "profile": {
            "name": f"{student.first_name} {student.last_name}",
            "roll_no": student.roll_no,
            "branch": academic.branch if academic else "N/A",
            "semester": current_sem
        },
        "stats": {
            "attendance": att_percentage,
            "cgpa": cgpa,
            "fee_dues": total_dues,
            "library_books": active_books_count
        },
        "ai_insight": ai_msg
    }

# ... (Keep existing profile, academic, and other routes as they are)

@router.get("/profile", response_model=StudentProfileResponse)
def view_profile(user=Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.put("/profile", response_model=StudentProfileResponse)
def save_or_update_profile(
    req: StudentProfileRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = user["sub"]
    student = upsert_student_profile(db, email, req)
    return student


@router.get("/my-academics")
def view_my_academics(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Academic).filter(Academic.user_email == user["sub"]).all()


@router.get("/payments")
def get_student_payments(
    semester: int, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)

    data = get_student_payment_details(
        db=db, student_email=user["sub"], semester=semester
    )
    print(data)
    if not data:
        raise HTTPException(status_code=404, detail="No payment data found")

    return data


@router.get("/internal-marks/{year}/{semester}")
def get_internal_marks(
    year: int,
    semester: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()
    return get_internal_marks_by_student(db, student.roll_no, year, semester)


@router.get("/external-marks/{year}/{semester}")
def get_external_marks(
    year: int,
    semester: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print(year, " sdf", semester)
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)
    externalmarks = get_semester_result(year, semester, db, user["sub"])

    return externalmarks


@router.get("/attendance/monthly")
def view_monthly_attendance(
    month: int, year: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()

    return get_student_monthly_attendance(
        db=db, student_id=student.id, month=month, year=year
    )


@router.get("/attendance/summary")
def attendance_summary(
    semester: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()
    return get_semester_attendance_summary(
        db=db, srno=student.roll_no, semester=semester
    )


@router.get("/attendance/subject-wise")
def subject_wise_attendance(
    semester: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()
    return get_subject_wise_attendance(db=db, srno=student.roll_no, semester=semester)


@router.get("/hostel")
def view_hostel(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_student_hostel_details(db, user["sub"])


from fastapi import Request

@router.get("/timetable")
def view_student_timetable(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    academic = (
        db.query(Academic)
        .filter(Academic.user_email == user["sub"])
        .first()
    )

    if not academic:
        return {"image_url": None}

    timetable = (
        db.query(TimeTable)
        .filter(
            TimeTable.year == academic.year,
            TimeTable.semester == academic.semester,
            TimeTable.section == academic.section,
            TimeTable.branch == academic.branch,
        )
        .first()
    )

    if not timetable:
        return {"image_url": None}

    image_url = str(request.base_url).rstrip("/") + "/" + timetable.image_path.replace("\\", "/")

    return {"image_url": image_url}


@router.get("/notifications")
def view_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "STUDENT":
        raise HTTPException(403, "Access denied")

    
    batch = db.query(Academic.batch).filter(Academic.user_email == current_user["sub"]).scalar()
    print("Student Batch:", batch)
    if not batch:
        raise HTTPException(404, "Student academic record not found")

    return get_student_notifications(db, current_user["sub"], batch)
@router.get("/alerts")
def get_my_alerts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students can view these alerts")

    # Get student roll no using their email
    student = db.query(Student).filter(Student.user_email == user["sub"]).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    alerts = (
        db.query(Alert)
        .filter(Alert.student_roll == student.roll_no)
        .order_by(Alert.created_at.desc())
        .all()
    )
    return alerts