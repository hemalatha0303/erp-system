from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class AttendanceItem(BaseModel):
    roll_no: str
    status: str  

class AttendanceCreate(BaseModel):
    subject_code: str
    subject_name: str
    year: Optional[int] = None
    semester: int
    date: date
    period: int
    batch: Optional[str] = None
    attendance: List[AttendanceItem]
    
