from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base


class CourseGrade(Base):
    """
    Course Grade table - stores calculated grades for each student-subject combination.
    
    This table aggregates:
    - Internal marks (30)
    - External marks (70)
    - Semester marks (0-100)
    - Grade letter and points
    """
    __tablename__ = "course_grades"

    id = Column(Integer, primary_key=True)
    
    # Student reference
    sid = Column(Integer, ForeignKey("students.id"))
    srno = Column(String(20))  # Roll number
    
    # Course info
    subject_code = Column(String(20))
    subject_name = Column(String(100))
    credits = Column(Integer)
    
    # Marks components
    internal_marks = Column(Float)  # Final internal (out of 30)
    external_marks = Column(Float)  # Exam marks (out of 70)
    semester_marks = Column(Float)  # Total (out of 100)
    
    # Grade info
    grade_letter = Column(String(2))  # A+, A, B, C, D, E, F, Ab
    grade_points = Column(Float)  # 10, 9, 8, 7, 6, 5, 0
    
    batch = Column(String(20))
    branch = Column(String(20))
    section = Column(String(5))
    semester = Column(Integer)


class SemesterGrade(Base):
    """
    Semester Grade table - stores SGPA and CGPA for students per semester.
    """
    __tablename__ = "semester_grades"

    id = Column(Integer, primary_key=True)
    
    # Student reference
    sid = Column(Integer, ForeignKey("students.id"))
    srno = Column(String(20))  # Roll number
    
    # Batch info
    batch = Column(String(20))
    branch = Column(String(20))
    section = Column(String(5))
    
    semester = Column(Integer)
    
    # Grade points
    sgpa = Column(Float)  # Semester GPA (up to 10.0)
    cgpa = Column(Float)  # Cumulative GPA (up to 10.0)
    cgpa_percentage = Column(Float)  # Equivalent percentage: (CGPA - 0.75) * 10
    
    # Credits
    total_credits = Column(Integer)
    
    # Status
    result_status = Column(String(10))  # PASS, FAIL, ABSENT
