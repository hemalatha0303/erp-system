from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base
class InternalMarks(Base):
    __tablename__ = "internal_marks"

    id = Column(Integer, primary_key=True)
    sid = Column(Integer)
    srno = Column(String(20))
    subject_code = Column(String(20))
    subject_name = Column(String(100))

    year = Column(Integer)
    semester = Column(Integer)

    openbook1 = Column(Integer)
    openbook2 = Column(Integer)
    descriptive1 = Column(Integer)
    descriptive2 = Column(Integer)
    seminar1 = Column(Integer)
    seminar2 = Column(Integer)
    objective1 = Column(Integer)
    objective2 = Column(Integer)

    entered_by = Column(String(100))
