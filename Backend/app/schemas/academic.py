from pydantic import BaseModel
from datetime import date

class AcademicResponse(BaseModel):
    srno: str
    branch: str
    batch: str
    course: str
    year: int
    semester: int
    section: str
    type: str
    quota: str | None
    admission_date: date
    status: str

    class Config:
        from_attributes = True
