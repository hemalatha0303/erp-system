from pydantic import BaseModel

class InternalMarksFetch(BaseModel):
    roll_no: str
    subject_name: str
    year: int
    semester: int


class InternalMarksUpdate(BaseModel):
    roll_no: str
    subject_name: str
    year: int
    semester: int
    subject_name: str
    openbook1: int
    openbook2: int
    descriptive1: int
    descriptive2: int
    seminar1: int
    seminar2: int
    objective1: int
    objective2: int
