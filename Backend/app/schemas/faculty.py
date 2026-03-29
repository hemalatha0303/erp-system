from pydantic import BaseModel
from typing import Optional

class FacultyProfileRequest(BaseModel):
    first_name: str
    last_name: str
    mobile_no: str
    address: str
    qualification: str
    experience: int
    personal_email: Optional[str] = None
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    branch: Optional[str] = None

class FacultyProfileResponse(FacultyProfileRequest):
    user_email: str
