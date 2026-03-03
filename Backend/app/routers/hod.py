from fastapi import Depends, Form, HTTPException
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.faculty_service import get_faculty_by_email, get_student_info_by_rollno
from app.services.timetable_service import upload_timetable_image
from fastapi import APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.academic import Academic
from app.models.internal_marks import InternalMarks
from app.schemas.hod import HODProfileResponse, HODProfileUpdate
from app.services.hod_service import get_hod_profile, update_hod_profile
from app.services.attendance_service import (
    get_semester_attendance_summary,

)
from app.models.alert import Alert
from app.schemas.alert import AlertCreate
router = APIRouter(prefix="/hod", tags=["HOD"])

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

    return upload_timetable_image(
        db, file, year, semester, branch, section, faculty_email, user["sub"]
    )

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
    year: int,
    semester: int,
    section: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "HOD":
        raise HTTPException(403, "Only HOD allowed")

    # Fetch students with optional internal marks
    results = db.query(Student, InternalMarks)\
        .join(Academic, Academic.sid == Student.id)\
        .outerjoin(
            InternalMarks,
            (InternalMarks.srno == Student.roll_no) &
            (InternalMarks.year == year) &
            (InternalMarks.semester == semester)
        )\
        .filter(
            Academic.year == year,
            Academic.semester == semester,
            Academic.section == section
        ).all()

    analytics = []
    for student, marks in results:
        # Calculate mids
        if marks:
            m1 = (
                (marks.descriptive1 or 0) * 15 / 30 +
                (marks.seminar1 or 0) * 5 / 5 +
                (marks.objective1 or 0) * 10 / 20 +
                (marks.openbook1 or 0) * 5 / 20
            )
            m2 = (
                (marks.descriptive2 or 0) * 15 / 30 +
                (marks.seminar2 or 0) * 5 / 5 +
                (marks.objective2 or 0) * 10 / 20 +
                (marks.openbook2 or 0) * 5 / 20
            )
        else:
            m1 = 0
            m2 = 0

        # Calculate attendance percentage
        att_summary = get_semester_attendance_summary(db, student.roll_no, semester)
        attendance_pct = att_summary["attendance_percentage"]

        analytics.append({
            "roll": student.roll_no,
            "name": f"{student.first_name} {student.last_name}",
            "m1": round(m1, 2),
            "m2": round(m2, 2),
            "att": f"{attendance_pct}%",  # from attendance calculation
            "ph": student.parent_mobile_no
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