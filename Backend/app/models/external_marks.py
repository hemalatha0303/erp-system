from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class ExternalMarks(Base):
    """
    External marks table - stores admin-uploaded semester exam marks.
    
    Admin uploads: rollno, subjectcode, subjectname, credits, externalmarks (70 marks)
    Grade is calculated and stored automatically.
    """
    __tablename__ = "external_marks"

    id = Column(Integer, primary_key=True)
    
    # Student reference
    sid = Column(Integer, ForeignKey("students.id"))
    srno = Column(String(20))  # Roll number
    
    # Course info
    subject_code = Column(String(20))
    subject_name = Column(String(100))
    credits = Column(Integer)  # Course credits
    
    # External marks (out of 70)
    external_marks = Column(Integer)
    
    # Batch info
    batch = Column(String(20))
    branch = Column(String(20))
    section = Column(String(5))
    
    semester = Column(Integer)
    
    # Calculated grade
    grade = Column(String(2))  # A+, A, B, C, D, E, F, Ab
    
    # Audit
    entered_by = Column(String(100))

