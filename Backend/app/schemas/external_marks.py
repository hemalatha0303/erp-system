from pydantic import BaseModel

class ExternalMarksCreate(BaseModel):
    roll_no: str
    subject_code: str
    semester: int
    subjectname: str
    grade: str
    credits: int
    gpa: float
