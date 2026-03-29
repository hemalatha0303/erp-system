from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.core.database import Base


class InternalMarks(Base):
    """
    Internal marks table - stores components and calculated mid exam marks.
    
    Faculty uploads: objective1, descriptive1, openbook1, seminar1, objective2, descriptive2, openbook2, seminar2
    Mid1 and Mid2 are calculated automatically:
    - Each component scaled: objective/2, descriptive/3, openbook/4, seminar/1
    - Total per mid = 30 marks
    
    NOTE: Year is derived from academic record + semester, no need to store redundantly
    """
    __tablename__ = "internal_marks"

    id = Column(Integer, primary_key=True)
    
    # Student and course info
    sid = Column(Integer, ForeignKey("students.id"))
    srno = Column(String(20))  # Roll number
    subject_code = Column(String(20))
    subject_name = Column(String(100))
    
    # Semester only (year derived from Academic table)
    semester = Column(Integer)
    
    # Mid 1 Components (from file)
    objective1 = Column(Integer)  # Out of 20
    descriptive1 = Column(Integer)  # Out of 30
    openbook1 = Column(Integer)  # Out of 20
    seminar1 = Column(Integer)  # Out of 5
    
    # Mid 2 Components (from file)
    objective2 = Column(Integer)  # Out of 20
    descriptive2 = Column(Integer)  # Out of 30
    openbook2 = Column(Integer)  # Out of 20
    seminar2 = Column(Integer)  # Out of 5
    
    # Calculated mid totals (out of 30 each)
    mid1 = Column(Float)  # Calculated: objective1/2 + descriptive1/3 + openbook1/4 + seminar1/1
    mid2 = Column(Float)  # Calculated: objective2/2 + descriptive2/3 + openbook2/4 + seminar2/1
    
    # Final internal marks (out of 30)
    final_internal_marks = Column(Float)  # Calculated: (Best*0.8 + Least*0.2)
    
    # Audit
    entered_by = Column(String(100))

