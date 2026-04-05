from fastapi import Depends, Form, HTTPException
from fastapi import APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.services.faculty_service import get_faculty_by_email, get_student_info_by_rollno
from app.services.timetable_service import upload_timetable_image
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.academic import Academic
from app.models.internal_marks import InternalMarks
from app.utils.marks_calculator import calc_mid_total
from app.models.payment import Payment
from app.schemas.hod import HODProfileResponse, HODProfileUpdate
from app.schemas.notification import NotificationCreate
from app.utils.validators import validate_vvit_and_format, validate_email_format
from app.services.notification_service import create_notification, get_hod_notifications
from app.services.hod_service import get_hod_profile, update_hod_profile
from app.services.attendance_service import (
    get_semester_attendance_summary,

)
from app.models.alert import Alert
from app.schemas.alert import AlertCreate

router = APIRouter(prefix="/hod", tags=["HOD"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/profile", response_model=HODProfileResponse)
def view_hod_profile(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "HOD":
        raise HTTPException(status_code=403, detail="Only HOD allowed")

    profile = get_hod_profile(db, user["sub"])
    if not profile:
        raise HTTPException(status_code=404, detail="HOD Profile not found")
    
    return profile

@router.put("/profile", response_model=HODProfileResponse)
def update_hod_profile_route(
    req: HODProfileUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "HOD":
        raise HTTPException(status_code=403, detail="Only HOD allowed")

    updated_profile = update_hod_profile(db, user["sub"], req)
    if not updated_profile:
        raise HTTPException(status_code=400, detail="Failed to update profile")

    return updated_profile

@router.get("/notifications")
def view_hod_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "HOD":
        raise HTTPException(status_code=403, detail="Only HOD allowed")
    return get_hod_notifications(db, user["sub"])

@router.post("/notifications")
def send_hod_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "HOD":
        raise HTTPException(status_code=403, detail="Only HOD allowed")
    if not validate_vvit_and_format(user["sub"]):
        raise HTTPException(status_code=400, detail="Sender must be a @vvit.net email")
    if data.target_email and not validate_email_format(data.target_email):
        raise HTTPException(status_code=400, detail="Invalid target email format")
    return create_notification(db, data, user["sub"], user["role"])

@router.post("/timetable/upload")
def upload_timetable(
    year: int = Form(...),
    semester: int = Form(...),
    branch: str = Form(...),
    section: str = Form(None),
    faculty_email: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "HOD":
        raise HTTPException(403, "Only HOD allowed")

    try:
        return upload_timetable_image(
            db, file, year, semester, branch, section, faculty_email, user["sub"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/faculty")
def get_department_faculty(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "HOD":
        raise HTTPException(403, "Only HOD allowed")
        
    faculty = db.query(Faculty).all()
    return [
        {
            "id": f.id,
            "name": f"{f.first_name} {f.last_name}",
            "email": f.user_email,
            "phno": f.mobile_no,
            "sub": f.qualification, 
        }
        for f in faculty
    ]

@router.get("/students-analytics")
def get_student_analytics(
    batch: str = None,
    branch: str = None,
    semester: str = None,
    section: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "HOD":
        raise HTTPException(403, "Only HOD allowed")
    # Normalize filters
    batch = batch.strip() if batch else None
    branch = None if not branch or branch.upper() == "ALL" else branch
    section = None if not section or section.upper() == "ALL" else section
    semester_val = None if not semester or semester.upper() == "ALL" else int(semester)

    # Build academic query
    if semester_val is None:
        # Use latest semester per student
        subq = (
            db.query(Academic.sid, func.max(Academic.semester).label("max_sem"))
            .group_by(Academic.sid)
            .subquery()
        )
        query = (
            db.query(Student, Academic)
            .join(subq, subq.c.sid == Student.id)
            .join(Academic, (Academic.sid == Student.id) & (Academic.semester == subq.c.max_sem))
        )
    else:
        query = (
            db.query(Student, Academic)
            .join(Academic, Academic.sid == Student.id)
            .filter(Academic.semester == semester_val)
        )

    if batch:
        query = query.filter(Academic.batch == batch)
    if branch:
        query = query.filter(Academic.branch == branch)
    if section:
        query = query.filter(Academic.section == section)

    results = query.all()

    analytics = []
    for student, academic in results:
        semester_used = semester_val or academic.semester

        marks = (
            db.query(InternalMarks)
            .filter(
                InternalMarks.sid == student.id,
                InternalMarks.semester == semester_used
            )
            .first()
        )

        if marks:
            m1 = marks.mid1 if marks.mid1 is not None else calc_mid_total(
                marks.openbook1, marks.objective1, marks.descriptive1, marks.seminar1
            )
            m2 = marks.mid2 if marks.mid2 is not None else calc_mid_total(
                marks.openbook2, marks.objective2, marks.descriptive2, marks.seminar2
            )
        else:
            m1 = 0
            m2 = 0

        att_summary = get_semester_attendance_summary(db, student.roll_no, semester_used)
        attendance_pct = att_summary["attendance_percentage"]

        analytics.append({
            "roll": student.roll_no,
            "name": f"{student.first_name} {student.last_name}",
            "m1": round(m1, 2),
            "m2": round(m2, 2),
            "att": f"{attendance_pct}%",
            "ph": student.parent_mobile_no,
            "branch": academic.branch,
            "section": academic.section,
            "semester": semester_used
        })

    return analytics


@router.get("/student/{roll_no}")
def hod_view_student_by_rollno(
    roll_no: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "HOD":
        raise HTTPException(status_code=403, detail="Only HOD allowed")

    data = get_student_info_by_rollno(db, roll_no)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")

    return data


@router.get("/student-list")
def get_comprehensive_student_list(
    year: int = None,
    semester: int = None,
    branch: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get comprehensive list of students with payment information for search/filter"""
    if user["role"] != "HOD":
        raise HTTPException(status_code=403, detail="Authorized for HOD only")

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
                "year": academic.year if academic else None,
                "semester": academic.semester if academic else None,
                "branch": academic.branch if academic else None,
                "section": academic.section if academic else None,
                "payment_records": payment_data,
            }
        )

    return result


@router.get("/view/faculty/{email}")
def view_faculty(
        email:str,
        user=Depends(get_current_user),
        db: Session =Depends(get_db)
                 ):
    if user["role"] != "HOD":
        raise HTTPException(status_code=403,detail="Only HOD Allowed")
    data= get_faculty_by_email(db,email)
    if not data:
        return HTTPException(status_code=404, detail="Faculty not found")
    return data
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

