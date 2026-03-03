from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    title: str
    message: str
    target_role: str        # STUDENT | ALL
    batch: Optional[str] = None
    category: str           # ACADEMIC | FEES | HOSTEL | LIBRARY | GENERAL
    priority: str           # CRITICAL | IMPORTANT | NORMAL

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    category: str
    priority: str
    created_at: datetime