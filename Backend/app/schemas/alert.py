from pydantic import BaseModel
from datetime import datetime

class AlertCreate(BaseModel):
    student_roll: str
    title: str
    message: str
    severity: str = "WARNING"

class AlertResponse(BaseModel):
    id: int
    sender_email: str
    sender_role: str
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True