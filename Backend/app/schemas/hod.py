from pydantic import BaseModel

class HODProfileUpdate(BaseModel):
    name: str
    department: str
    mobile_no: str
    qualification: str
    experience: int

class HODProfileResponse(HODProfileUpdate):
    email: str
