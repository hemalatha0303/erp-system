from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    title: str
    message: str
    target_role: str        # STUDENT | FACULTY | HOD | ALL
    batch: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None
    target_email: Optional[str] = None
    category: str           # ACADEMIC | FEES | HOSTEL | LIBRARY | GENERAL
    priority: str           # CRITICAL | IMPORTANT | NORMAL

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    category: str
    priority: str
    target_role: Optional[str] = None
    batch: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None
    target_email: Optional[str] = None
    sender_role: Optional[str] = None
    created_at: datetime
