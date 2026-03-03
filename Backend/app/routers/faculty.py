from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.models.student import Student
from app.models.timetable import TimeTable
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
    year: int,
    semester: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

    upload_internal_marks_excel(
        db=db,
        file=file,
        subject_code=subject_code,
        year=year,
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
    return get_internal_marks(db, req)


@router.put("/internal-marks/update")
def update_marks(
    req: InternalMarksUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    update_internal_marks(db, req)
    return {"message": "Internal marks updated successfully"}


@router.post("/attendance/mark")
def mark_attendance_api(
    req: AttendanceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Only faculty allowed")

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
    year: int,
    semester: int,
    section: str,
    branch: str = "CSE",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "FACULTY":
        raise HTTPException(status_code=403, detail="Authorized for Faculty only")

    results = (
        db.query(Student.roll_no, Student.first_name, Student.last_name)
        .join(Academic, Academic.sid == Student.id)
        .filter(
            Academic.year == year,
            Academic.semester == semester,
            Academic.section == section,
            Academic.branch == branch,
        )
        .all()
    )

    return [
        {"roll_no": r.roll_no, "name": f"{r.first_name} {r.last_name}"} for r in results
    ]

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