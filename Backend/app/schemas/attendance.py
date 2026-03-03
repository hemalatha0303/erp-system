from pydantic import BaseModel
from typing import List
from datetime import date

class AttendanceItem(BaseModel):
    roll_no: str
    status: str  

class AttendanceCreate(BaseModel):
    subject_code: str
    subject_name: str
    year: int
    semester: int
    date: date
    period: int
    attendance: List[AttendanceItem]
    