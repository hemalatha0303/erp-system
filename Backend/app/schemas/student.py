from pydantic import BaseModel
from datetime import date

class StudentProfileRequest(BaseModel):
    roll_no: str
    first_name: str
    last_name: str
    gender: str
    blood_group: str
    date_of_birth: date
    mobile_no: str
    parent_mobile_no: str
    address: str
    parentname: str
from pydantic import BaseModel
from typing import Optional
from datetime import date

class StudentProfileResponse(BaseModel):
    roll_no: str
    first_name: str
    last_name: str

    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    parentname: Optional[str] = None

    class Config:
        from_attributes = True   

