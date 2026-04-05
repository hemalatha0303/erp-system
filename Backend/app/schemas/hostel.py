
from pydantic import BaseModel
from typing import Optional


class HostelRoomCreate(BaseModel):
    room_number: str
    sharing: int
    room_type: str
    capacity: int


class HostelRoomUpdate(BaseModel):
    sharing: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None


class HostelAllocateRequest(BaseModel):
    roll_no: str
    room_number: str


class AllocateFromUI(BaseModel):
    student_id: int
    room_id: int


class UpdateAllocationStatus(BaseModel):
    allocation_id: int
    status: str  # ALLOCATED, VACATED, NOT_ALLOCATED

