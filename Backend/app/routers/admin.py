from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.notification import NotificationCreate
from app.utils.validators import validate_vvit_and_format, validate_email_format
from app.services.notification_service import create_notification
from app.services.notification_service import create_notification
from app.schemas.hostel import (
    HostelAllocateRequest, 
    HostelRoomCreate,
    HostelRoomUpdate,
    AllocateFromUI,
    UpdateAllocationStatus
)
from app.services.excel_service import process_excel
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.fee_structure import FeeStructureCreate
from app.services.fee_structure_service import create_fee_structure
from app.schemas.fee_structure import FeeStructureBulkCreate
from app.services.fee_structure_service import bulk_create_fee_structure
from app.schemas.external_marks import ExternalMarksCreate
from app.services.excel_marks_service import upload_external_marks_excel
from app.services.hostel_service import (
    allocate_student_hostel, 
    upload_hostel_rooms_excel, 
    vacate_hostel_room,
    get_hostel_statistics,
    get_all_hostel_rooms,
    get_all_hostel_allocations,
    create_hostel_room,
    update_hostel_room,
    delete_hostel_room,
    update_allocation_status,
    allocate_student_to_hostel_ui
)
from app.models.student import Student
from app.models.academic import Academic
from sqlalchemy import func
from app.models.faculty import Faculty
from app.models.hod import HODProfile
from app.models.payment import Payment
from app.schemas.admin import AdminProfileUpdate
from app.services.admin_service import get_admin_profile, update_admin_profile
router = APIRouter(prefix="/admin")
@router.get("/get-profile")
def view_admin_profile(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    profile = get_admin_profile(db, user["sub"])
    if not profile:
        raise HTTPException(status_code=404, detail="Admin profile not found")
    return profile


@router.put("/update-profile")
def update_admin(
    data: AdminProfileUpdate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    updated = update_admin_profile(db, user["sub"], data)
    if not updated:
        raise HTTPException(status_code=404, detail="Admin profile not found")
    return {"message": "Admin profile updated successfully"}

@router.post("/upload-students")
def upload_excel(
    file: UploadFile = File(...),
    role: str = Query("STUDENT", description="STUDENT, FACULTY, or HOD"),
    semester: int = Query(1, description="Semester for students"),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        process_excel(file, db, user["sub"], role=role, selected_semester=semester)
        return {
            "success": True,
            "message": f"Excel uploaded successfully for {role}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)[:100]}"
        )

@router.post("/fee-structure")
def add_fee_structure(
    req: FeeStructureCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    success, msg = create_fee_structure(db, req.dict())
    if not success:
        raise HTTPException(status_code=400, detail=msg)

    return {"message": msg}


@router.post("/fee-structure/bulk")
def bulk_fee_structure(
    req: FeeStructureBulkCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    msg = bulk_create_fee_structure(db, [i.dict() for i in req.items])
    return {"message": msg}


@router.post("/external-marks/upload/{batch}/{semester}")
def upload_external_marks(
    batch: str,
    semester: int,
    file: UploadFile,
    branch: str = None,
    section: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        upload_external_marks_excel(db, file, batch, semester, user["sub"], branch=branch, section=section)
        return {"message": "External marks Excel uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/hostel/rooms/upload")
def upload_hostel_rooms(
    file: UploadFile,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")

    upload_hostel_rooms_excel(db, file)

    return {"message": "Hostel rooms uploaded successfully"}


@router.post("/hostel/allocate")
def allocate(req: HostelAllocateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    allocate_student_hostel(db, req, user["sub"])
    return {"message": "Student allocated"}
@router.post("/hostel/room/vacate")
def vacate_room(req: HostelAllocateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")

    vacate_hostel_room(db, req, user["sub"])
    return {"message": "Student vacated"}

# ==================== NEW HOSTEL MANAGEMENT ENDPOINTS ====================

@router.get("/hostel/statistics")
def get_hostel_stats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get hostel statistics: total rooms, allocated, vacated, not allocated"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        stats = get_hostel_statistics(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/hostel/rooms")
def get_hostel_rooms(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all hostel rooms"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        rooms = get_all_hostel_rooms(db)
        return {"rooms": rooms}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/hostel/allocations")
def get_hostel_allocations(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all hostel allocations with student and room details"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        allocations = get_all_hostel_allocations(db)
        return {"allocations": allocations}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/hostel/room/create")
def create_hostel_room_endpoint(
    req: HostelRoomCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Create a new hostel room"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        room = create_hostel_room(db, req.room_number, req.sharing, req.room_type, req.capacity)
        return {
            "message": "Room created successfully",
            "room_id": room.id,
            "room_number": room.room_number
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/hostel/room/{room_id}")
def update_hostel_room_endpoint(
    room_id: int,
    req: HostelRoomUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Update hostel room details"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        room = update_hostel_room(db, room_id, req.sharing, req.room_type, req.capacity)
        return {"message": "Room updated successfully", "room_id": room.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/hostel/room/{room_id}")
def delete_hostel_room_endpoint(
    room_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Delete (soft delete) a hostel room"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        delete_hostel_room(db, room_id)
        return {"message": "Room deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/hostel/allocation/create")
def allocate_student_hostel_ui(
    req: AllocateFromUI,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Allocate student to hostel room from UI"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        allocation = allocate_student_to_hostel_ui(db, req.student_id, req.room_id, user["sub"])
        return {
            "message": "Student allocated successfully",
            "allocation_id": allocation.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/hostel/allocation/{allocation_id}/status")
def update_allocation_status_endpoint(
    allocation_id: int,
    req: UpdateAllocationStatus,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Update allocation status (ALLOCATED/VACATED/NOT_ALLOCATED)"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        allocation = update_allocation_status(db, allocation_id, req.status, user["sub"])
        return {
            "message": f"Allocation status updated to {req.status}",
            "allocation_id": allocation.id,
            "status": allocation.status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/students")
def get_all_students(
    search: str = None,
    branch: str = None,
    year: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    query = db.query(Student, Academic).join(Academic, Academic.sid == Student.id)

    if search:
        query = query.filter(
            (Student.roll_no.contains(search)) | 
            (Student.first_name.contains(search))
        )
    if branch and branch != "All":
        query = query.filter(Academic.branch == branch)
    if year and year != "All": 
        query = query.filter(Academic.year == int(year))

    results = query.limit(100).all() 

    return [
        {
            "id": s.id,
            "roll_no": s.roll_no,
            "name": f"{s.first_name} {s.last_name}",
            "first_name": s.first_name,
            "last_name": s.last_name,
            "email": s.user_email,
            "gender": s.gender,
            "mobile": s.mobile_no,
            "parent_mobile": s.parent_mobile_no,
            "address": s.address,
            "parentname": s.parentname,
            "blood_group": s.blood_group,
            "date_of_birth": str(s.date_of_birth) if s.date_of_birth else None,
            "residence_type": s.residence_type,
            "branch": a.branch,
            "year": a.year,
            "semester": a.semester,
            "section": a.section,
            "batch": a.batch,
            "course": a.course,
            "quota": a.quota,
            "admission_date": str(a.admission_date) if a.admission_date else None,
            "status": a.status
        }
        for s, a in results
    ]

@router.get("/faculty")
def get_all_faculty(
    search: str = None,
    branch: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    query = db.query(Faculty)

    if search:
        query = query.filter(
            (Faculty.first_name.contains(search)) | 
            (Faculty.last_name.contains(search)) |
            (Faculty.user_email.contains(search))
        )
    if branch and branch != "All":
        query = query.filter(Faculty.branch == branch)

    results = query.limit(100).all()

    return [
        {
            "id": f.id,
            "name": f"{f.first_name} {f.last_name}",
            "first_name": f.first_name,
            "last_name": f.last_name,
            "email": f.user_email,
            "personal_email": f.personal_email,
            "mobile": f.mobile_no,
            "mobile_no": f.mobile_no,
            "address": f.address,
            "qualification": f.qualification,
            "experience": f.experience,
            "years_of_experience": f.experience,
            "subject_code": f.subject_code,
            "subject_name": f.subject_name,
            "branch": f.branch
        }
        for f in results
    ]

@router.get("/hods")
def get_all_hods(
    search: str = None,
    branch: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    query = db.query(HODProfile)

    if search:
        query = query.filter(
            (HODProfile.first_name.contains(search)) | 
            (HODProfile.last_name.contains(search)) |
            (HODProfile.email.contains(search))
        )
    if branch and branch != "All":
        query = query.filter(HODProfile.branch == branch)

    results = query.limit(100).all()

    return [
        {
            "id": h.id,
            "name": f"{h.first_name or ''} {h.last_name or ''}".strip(),
            "first_name": h.first_name,
            "last_name": h.last_name,
            "email": h.email,
            "personal_email": h.personal_email,
            "mobile": h.mobile_no,
            "mobile_no": h.mobile_no,
            "address": h.address,
            "qualification": h.qualification,
            "experience": h.experience,
            "years_of_experience": h.experience,
            "branch": h.branch
        }
        for h in results
    ]

@router.get("/hostel/students")
def get_hosteler_students(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all hosteler students for allocation"""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")
    
    try:
        students = db.query(Student, Academic).join(
            Academic, Academic.sid == Student.id
        ).filter(
            Student.residence_type == "HOSTELER"
        ).all()
        
        students_data = []
        for student, academic in students:
            students_data.append({
                "id": student.id,
                "roll_no": student.roll_no,
                "name": f"{student.first_name} {student.last_name}",
                "year": academic.year,
                "branch": academic.branch,
                "section": academic.section
            })
        
        return {"students": students_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admin allowed")

    
    total_students = db.query(Student).count()

    
    active_faculty = db.query(Faculty).count()

    
    total_fees = db.query(func.sum(Payment.amount_paid)).scalar() or 0
    print(total_fees)
    
    
    admitted_ids = db.query(Academic.sid).distinct()
    pending_admissions = db.query(Student).filter(Student.id.notin_(admitted_ids)).count()

    return {
        "total_students": total_students,
        "active_faculty": active_faculty,
        "fees_collected": total_fees,
        "pending_admissions": pending_admissions
    }

@router.get("/dashboard/activity")
def get_recent_activity(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admin allowed")

    activity_log = []

    
    recent_students = db.query(Student).order_by(Student.id.desc()).limit(3).all()
    for s in recent_students:
        activity_log.append({
            "action": "New Student Joined",
            "user": f"{s.first_name} {s.last_name}",
            "time": "Recently" 
        })

    
    recent_payments = db.query(Payment).order_by(Payment.id.desc()).limit(3).all()
    for p in recent_payments:
        activity_log.append({
            "action": f"Fee Payment ({p.fee_type})",
            "user": p.srno, 
            "time": str(p.payment_date)
        })

    return activity_log

@router.post("/notifications")
def send_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(403, "Access denied")

    if not validate_vvit_and_format(current_user["sub"]):
        raise HTTPException(status_code=400, detail="Sender must be a @vvit.net email")
    if data.target_email and not validate_email_format(data.target_email):
        raise HTTPException(status_code=400, detail="Invalid target email format")

    return create_notification(db, data, current_user["sub"], current_user["role"])
