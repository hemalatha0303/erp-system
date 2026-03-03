from pydantic import BaseModel
from datetime import date

class FacultyProfileRequest(BaseModel):
    first_name: str
    last_name: str
    gender: str
    blood_group: str
    date_of_birth: date
    mobile_no: str
    address: str
    qualification: str
    experience: int

class FacultyProfileResponse(FacultyProfileRequest):
    user_email: str
