from pydantic import BaseModel
from typing import Optional

class InternalMarksFetch(BaseModel):
    roll_no: str
    subject_name: str
    subject_code: Optional[str] = None
    semester: int
    batch: Optional[str] = None
    year: Optional[int] = None


class InternalMarksUpdate(BaseModel):
    roll_no: str
    subject_name: str
    subject_code: Optional[str] = None
    semester: int
    year: Optional[int] = None
    objective1: int
    objective2: int
    descriptive1: int
    descriptive2: int
    openbook1: int
    openbook2: int
    seminar1: int
    seminar2: int
    batch: Optional[str] = None
