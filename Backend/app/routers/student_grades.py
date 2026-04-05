"""
API endpoints for students to view their marks and grades.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.student import Student
from app.models.internal_marks import InternalMarks
from app.models.external_marks import ExternalMarks
from app.models.course_grade import CourseGrade, SemesterGrade
from app.utils.marks_calculator import cgpa_to_percentage


router = APIRouter(prefix="/student", tags=["student-grades"])


@router.get("/marks/internal/{semester}")
def get_internal_marks(
    semester: int,
    mid: int = 1,  # 1 for Mid1, 2 for Mid2
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get student's internal marks for a specific semester and mid exam.
    
    Returns: subject_code, subject_name, objective, descriptive, openbook, seminar, mid_marks
    """
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)
    
    student = db.query(Student).filter(
        Student.user_email == user["sub"]
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        marks = db.query(InternalMarks).filter(
            InternalMarks.sid == student.id,
            InternalMarks.semester == semester
        ).all()
        
        result = []
        for mark in marks:
            if mid == 1:
                result.append({
                    "subject_code": mark.subject_code,
                    "subject_name": mark.subject_name,
                    "objective": mark.objective1,
                    "descriptive": mark.descriptive1,
                    "openbook": mark.openbook1,
                    "seminar": mark.seminar1,
                    "mid_marks": mark.mid1,
                    "mid_max": 30
                })
            elif mid == 2:
                result.append({
                    "subject_code": mark.subject_code,
                    "subject_name": mark.subject_name,
                    "objective": mark.objective2,
                    "descriptive": mark.descriptive2,
                    "openbook": mark.openbook2,
                    "seminar": mark.seminar2,
                    "mid_marks": mark.mid2,
                    "mid_max": 30
                })
        
        return {
            "semester": semester,
            "mid": mid,
            "total_subjects": len(result),
            "marks": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/marks/external/{semester}")
def get_external_marks(
    semester: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get student's external marks (exam results) for a specific semester.
    
    Returns: subject_code, subject_name, credits, external_marks, grade, semester_marks
    """
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)
    
    student = db.query(Student).filter(
        Student.user_email == user["sub"]
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Get course grades which have all calculated marks
        course_grades = db.query(CourseGrade).filter(
            CourseGrade.sid == student.id,
            CourseGrade.semester == semester
        ).all()
        
        result = []
        total_credits = 0
        total_grade_points = 0
        
        for cg in course_grades:
            result.append({
                "subject_code": cg.subject_code,
                "subject_name": cg.subject_name,
                "credits": cg.credits,
                "internal_marks": cg.internal_marks,
                "external_marks": cg.external_marks,
                "semester_marks": cg.semester_marks,
                "grade": cg.grade_letter,
                "grade_points": cg.grade_points
            })
            total_credits += cg.credits
            total_grade_points += cg.grade_points * cg.credits
        
        # Get semester grade for SGPA and CGPA
        semester_grade = db.query(SemesterGrade).filter(
            SemesterGrade.sid == student.id,
            SemesterGrade.semester == semester
        ).first()
        
        sgpa = semester_grade.sgpa if semester_grade else 0.0
        cgpa = semester_grade.cgpa if semester_grade else 0.0
        cgpa_percentage = semester_grade.cgpa_percentage if semester_grade else 0.0
        
        return {
            "semester": semester,
            "total_subjects": len(result),
            "total_credits": total_credits,
            "marks": result,
            "sgpa": sgpa,  # Semester GPA
            "cgpa": cgpa,  # Cumulative GPA (all semesters)
            "cgpa_percentage": cgpa_percentage,
            "result_status": semester_grade.result_status if semester_grade else "PENDING"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transcript")
def get_academic_transcript(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get complete academic transcript for student.
    Shows all semesters with SGPA and overall CGPA.
    """
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)
    
    student = db.query(Student).filter(
        Student.user_email == user["sub"]
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Get all semester grades
        semester_grades = db.query(SemesterGrade).filter(
            SemesterGrade.sid == student.id
        ).order_by(SemesterGrade.semester).all()
        
        semesters = []
        overall_cgpa = 0.0
        
        for sem in semester_grades:
            study_year = max(1, (sem.semester + 1) // 2) if sem.semester else 1
            semesters.append({
                "semester": sem.semester,
                "year": study_year,
                "sgpa": sem.sgpa,
                "total_credits": sem.total_credits,
                "status": sem.result_status
            })
            overall_cgpa = sem.cgpa  # Latest CGPA
        
        return {
            "student_name": f"{student.first_name} {student.last_name}",
            "roll_number": student.roll_no,
            "total_semesters": len(semesters),
            "semesters": semesters,
            "overall_cgpa": overall_cgpa,
            "cgpa_percentage": cgpa_to_percentage(overall_cgpa)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/semester-results/{semester}")
def get_semester_results(
    semester: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get complete semester results with detailed breakdown.
    Includes internal, external, grades, and SGPA.
    """
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)
    
    student = db.query(Student).filter(
        Student.user_email == user["sub"]
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Get course grades for this semester
        course_grades = db.query(CourseGrade).filter(
            CourseGrade.sid == student.id,
            CourseGrade.semester == semester
        ).order_by(CourseGrade.subject_code).all()
        
        # Get internal marks details
        internal_marks = db.query(InternalMarks).filter(
            InternalMarks.sid == student.id,
            InternalMarks.semester == semester
        ).all()
        
        internal_map = {im.subject_code: im for im in internal_marks}
        
        subjects = []
        for cg in course_grades:
            im = internal_map.get(cg.subject_code)
            
            subjects.append({
                "subject_code": cg.subject_code,
                "subject_name": cg.subject_name,
                "credits": cg.credits,
                "mid1_marks": im.mid1 if im else 0,
                "mid2_marks": im.mid2 if im else 0,
                "internal_marks": cg.internal_marks,
                "external_marks": cg.external_marks,
                "semester_marks": cg.semester_marks,
                "grade": cg.grade_letter,
                "grade_points": cg.grade_points
            })
        
        # Get semester grade info
        sem_grade = db.query(SemesterGrade).filter(
            SemesterGrade.sid == student.id,
            SemesterGrade.semester == semester
        ).first()
        
        return {
            "semester": semester,
            "subjects": subjects,
            "total_subjects": len(subjects),
            "sgpa": sem_grade.sgpa if sem_grade else 0.0,
            "cgpa": sem_grade.cgpa if sem_grade else 0.0,
            "cgpa_percentage": sem_grade.cgpa_percentage if sem_grade else 0.0,
            "result_status": sem_grade.result_status if sem_grade else "PENDING"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
