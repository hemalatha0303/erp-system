from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.models.student import Student
from app.models.timetable import TimeTable
from app.models.payment import Payment
from app.schemas.faculty import FacultyProfileRequest, FacultyProfileResponse
from app.services.faculty_service import get_faculty_by_email, upsert_faculty_profile
from app.services.faculty_service import get_student_info_by_rollno
from app.schemas.internal_marks import InternalMarksFetch, InternalMarksUpdate
from app.services.internal_marks_service import (
    update_internal_marks,
    get_internal_marks,
)
from app.services.excel_marks_service import upload_internal_marks_excel
from app.schemas.attendance import AttendanceCreate
from app.services.attendance_service import get_student_attendance, mark_attendance
from app.models.student import Student
from app.models.academic import Academic
from app.models.alert import Alert
from app.schemas.alert import AlertCreate
from app.schemas.notification import NotificationCreate
from app.services.notification_service import get_faculty_notifications, create_notification
from app.utils.validators import validate_vvit_and_format, validate_email_format
from app.utils.academic_year import resolve_year
router = APIRouter(prefix="/faculty", tags=["Faculty"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/get-profile", response_model=FacultyProfileResponse)
def view_profile(user=Depends(get_current_user), db: Session = Depends(get_db)):
    print("here in ")
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403)

    faculty = get_faculty_by_email(db, user["sub"])
    print(faculty)
    if not faculty:
        raise HTTPException(status_code=404, detail="Profile not found")
    return faculty


@router.put("/profile", response_model=FacultyProfileResponse)
def update_profile(
    req: FacultyProfileRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403)

    return upsert_faculty_profile(db, user["sub"], req)


@router.get("/student/{roll_no}")
def faculty_view_student_by_rollno(
    roll_no: str, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

    data = get_student_info_by_rollno(db, roll_no)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")

    return data


@router.post("/internal-marks/upload")
def upload_internal_marks(
    subject_code: str,
    semester: int,
    file: UploadFile,
    batch: str = None,
    year: int = None,
    branch: str = None,
    section: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

    resolved_year = resolve_year(batch=batch, semester=semester, year=year)

    upload_internal_marks_excel(
        db=db,
        file=file,
        subject_code=subject_code,
        year=resolved_year,
        semester=semester,
        faculty_email=user["sub"],
    )

    return {"message": "Internal marks uploaded successfully"}


@router.post("/internal-marks/get")
def fetch_internal_marks(
    req: InternalMarksFetch,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    resolved_year = resolve_year(batch=req.batch, semester=req.semester, year=req.year)
    req.year = resolved_year
    return get_internal_marks(db, req)


@router.put("/internal-marks/update")
def update_marks(
    req: InternalMarksUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    resolved_year = resolve_year(batch=req.batch, semester=req.semester, year=req.year)
    req.year = resolved_year
    update_internal_marks(db, req)
    return {"message": "Internal marks updated successfully"}


@router.post("/attendance/mark")
def mark_attendance_api(
    req: AttendanceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

    resolved_year = resolve_year(batch=req.batch, semester=req.semester, year=req.year)
    req.year = resolved_year
    mark_attendance(db, req, user["sub"])
    return {"message": "Attendance marked successfully"}


@router.get("/attendance")
def view_attendance(
    Subject_code: str,
    srno: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.roll_no == srno).first()

    return get_student_attendance(db, student.id, Subject_code)


@router.get("/timetable")
def view_faculty_timetable(
    request: Request,          
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    timetable = db.query(TimeTable).filter(
        TimeTable.faculty_email == user["sub"]
    ).first()

    if not timetable:
        return {"image_url": None}

    image_url = (
        str(request.base_url).rstrip("/") + "/" +
        timetable.image_path.replace("\\", "/")
    )

    return {
        "image_url": str(image_url)
    }


@router.get("/class-students")
def get_students_by_class(
    batch: str,
    branch: str = "ALL",
    section: str = "ALL",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Authorized for Faculty only")

    query = (
        db.query(Student.roll_no, Student.first_name, Student.last_name)
        .join(Academic, Academic.sid == Student.id)
        .filter(Academic.batch == batch)
    )

    if branch and branch.upper() != "ALL":
        query = query.filter(Academic.branch == branch.upper())
    if section and section.upper() != "ALL":
        query = query.filter(Academic.section == section.upper())

    results = query.distinct(Student.roll_no).all()

    return [
        {"roll_no": r.roll_no, "name": f"{r.first_name} {r.last_name}"} for r in results
    ]


@router.get("/notifications")
def view_faculty_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

    faculty = get_faculty_by_email(db, user["sub"])
    branch = faculty.branch if faculty else None
    return get_faculty_notifications(db, user["sub"], branch)


@router.post("/notifications")
def send_faculty_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

    if not validate_vvit_and_format(user["sub"]):
        raise HTTPException(status_code=400, detail="Invalid sender email format")
    if data.target_email and not validate_email_format(data.target_email):
        raise HTTPException(status_code=400, detail="Invalid target email format")

    if data.target_role != "STUDENT":
        raise HTTPException(status_code=400, detail="Faculty can send notifications only to students")

    if not data.batch:
        raise HTTPException(status_code=400, detail="Batch is required for student notifications")

    if data.branch and str(data.branch).upper() == "ALL":
        data.branch = None
    if data.section and str(data.section).upper() == "ALL":
        data.section = None
    if data.branch:
        data.branch = data.branch.upper()
    if data.section:
        data.section = data.section.upper()

    create_notification(db, data, sender_email=user["sub"], sender_role="FACULTY")
    return {"message": "Notification sent successfully"}


@router.get("/student-list")
def get_comprehensive_student_list(
    year: int = None,
    semester: int = None,
    branch: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get comprehensive list of students with payment information for search/filter"""
    try:
        if user["role"] != "FACULTY":
            raise HTTPException(status_code=403, detail="Authorized for Faculty only")

        query = db.query(Student).join(Academic, Academic.sid == Student.id)

        if year:
            query = query.filter(Academic.year == year)
        if semester:
            query = query.filter(Academic.semester == semester)
        if branch:
            query = query.filter(Academic.branch == branch)

        students = query.all()
        result = []

        for student in students:
            academic = (
                db.query(Academic)
                .filter(Academic.sid == student.id)
                .order_by(Academic.year.desc())
                .first()
            )

            # Get payment records
            payment_records = db.query(Payment).filter(Payment.srno == student.roll_no).all()
            payment_data = [
                {
                    "fee_type": p.fee_type,
                    "status": p.status,
                    "amount_paid": p.amount_paid or 0,
                    "total_amount": getattr(p, "amount", 0) or 0,
                }
                for p in payment_records
            ]

            result.append(
                {
                    "roll_no": student.roll_no,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "mobile_no": student.mobile_no,
                    "email": student.user_email,
                    "status": academic.status if academic else None,
                    "residence_type": student.residence_type,
                    "quota": student.quota or "General",
                    "parent_mobile_no": student.parent_mobile_no or "",
                    "year": academic.year if academic else None,
                    "semester": academic.semester if academic else None,
                    "branch": academic.branch if academic else student.branch,
                    "section": academic.section if academic else student.section,
                    "batch": academic.batch if academic else student.batch,
                    "payment_records": payment_data,
                }
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in student-list endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch students: {str(e)}")


@router.post("/alerts/send")
def send_alert(
    alert_req: AlertCreate, 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if user["role"] not in ["FACULTY", "HOD"]:
        raise HTTPException(status_code=403, detail="Unauthorized to send alerts")

    new_alert = Alert(
        sender_email=user["sub"],
        sender_role=user["role"],
        student_roll=alert_req.student_roll,
        title=alert_req.title,
        message=alert_req.message,
        severity=alert_req.severity
    )
    db.add(new_alert)
    db.commit()
    return {"message": "Alert sent to student successfully!"}
