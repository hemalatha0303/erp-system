from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.student import Student
from app.services.attendance_service import get_low_subjects
from app.services.ai_service import get_attendance_advice

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