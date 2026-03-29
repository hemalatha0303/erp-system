from pydantic import BaseModel
from datetime import time

class TimeTableCreate(BaseModel):
    year: int
    semester: int
    section: str
    day: str
    period_no: int
    start_time: time
    end_time: time
    subject_code: str
    subject_name: str
    faculty_email: str
class StudentTimeTableResponse(BaseModel):
    day: str
    period_no: int
    start_time: time
    end_time: time
    subject_name: str
    faculty_email: str
class FacultyTimeTableResponse(BaseModel):
    day: str
    period_no: int
    start_time: time
    end_time: time
    subject_name: str
    section: str
