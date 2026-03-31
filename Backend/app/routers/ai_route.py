from fastapi import Depends, APIRouter, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.student import Student
from app.services.attendance_service import get_low_subjects
from app.services.ai_service import get_attendance_advice
from app.services.aews_service import AEWSService

router = APIRouter(prefix="/ai", tags=["AI Services"])

@router.get("/student/attendance/ai-advice")
def attendance_ai_advice(
    semester: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    
    student = db.query(Student).filter(
        Student.user_email == user["sub"]
    ).first()

    if not student:
        return {"message": "Student not found"}

    
    low_attendance = get_low_subjects(
        db=db,
        srno=student.roll_no,
        semester=semester
    )

    
    if not low_attendance:
        return {
            "message": "🎉 Your attendance is good in all subjects!",
            "eligible_for_exam": True
        }

    
    ai_message = get_attendance_advice(low_attendance)

    return {
        "eligible_for_exam": False,
        "low_attendance": low_attendance,
        "ai_message": ai_message
    }


# ===================================
# ACADEMIC EARLY WARNING SYSTEM (AEWS)
# ===================================

# TEST ENDPOINT (No auth required - for development/testing)
@router.get("/aews/test/student-risk/{roll_no}")
def test_get_student_risk(
    roll_no: str,
    semester: int = Query(1),
    db: Session = Depends(get_db)
):
    """
    TEST ENDPOINT - No authentication required
    Use this to test AEWS without login
    """
    risk_result = AEWSService.predict_student_risk(db, roll_no, semester)
    return risk_result


@router.get("/aews/student-risk/{roll_no}")
def get_student_risk(
    roll_no: str,
    semester: int = Query(1),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get academic risk assessment for a student
    
    Returns:
        - risk_level: HIGH, MEDIUM, or LOW
        - risk_probability: Percentage (0-100)
        - explanation: Human-readable explanation
        - factors: Detailed breakdown of risk factors
    """
    risk_result = AEWSService.predict_student_risk(db, roll_no, semester)
    return risk_result


# TEST ENDPOINT (No auth required - for development/testing)
@router.get("/aews/test/batch-at-risk")
def test_get_batch_at_risk_students(
    batch: str,
    semester: int = Query(1),
    branch: str = Query(None),
    section: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    TEST ENDPOINT - No authentication required
    Get list of at-risk students in a batch for testing
    """
    at_risk = AEWSService.get_at_risk_students(
        db, batch, semester, branch, section
    )
    return {
        "batch": batch,
        "semester": semester,
        "branch": branch,
        "section": section,
        "at_risk_count": len(at_risk),
        "students": at_risk
    }


@router.get("/aews/batch-at-risk")
def get_batch_at_risk_students(
    batch: str,
    semester: int = Query(1),
    branch: str = Query(None),
    section: str = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get list of at-risk students in a batch for HoD monitoring
    
    Returns:
        List of students with HIGH or MEDIUM risk sorted by risk probability
    """
    at_risk = AEWSService.get_at_risk_students(
        db, batch, semester, branch, section
    )
    return {
        "batch": batch,
        "semester": semester,
        "branch": branch,
        "section": section,
        "at_risk_count": len(at_risk),
        "students": at_risk
    }
