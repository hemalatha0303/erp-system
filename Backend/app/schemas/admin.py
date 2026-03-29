
from pydantic import BaseModel

class AdminProfileUpdate(BaseModel):
    name: str
    mobile_no: str
    designation: str

class AdminProfileResponse(AdminProfileUpdate):
    email: str