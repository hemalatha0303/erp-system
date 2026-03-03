
from pydantic import BaseModel


class HostelRoomCreate(BaseModel):
    room_number: str
    sharing: int
    room_type: str
    capacity: int


class HostelAllocateRequest(BaseModel):
    roll_no: str
    room_number: str
