from pydantic import BaseModel
from typing import Optional

class HODProfileUpdate(BaseModel):
    mobile_no: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_email: Optional[str] = None
    address: Optional[str] = None
    branch: Optional[str] = None

class HODProfileResponse(HODProfileUpdate):
    email: str
