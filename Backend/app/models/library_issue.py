
from app.core.database import Base

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from datetime import date
class LibraryIssue(Base):
    __tablename__ = "library_issue"

    id = Column(Integer, primary_key=True, index=True)
    srno = Column(String(20), nullable=False)
    book_code = Column(String(20), ForeignKey("library_books.code"))
    semester = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    issued_date = Column(Date, default=date.today)
    return_date = Column(Date, nullable=True)
    expected_return_date = Column(Date, nullable=False)
    status = Column(String(20), default="ISSUED")
    updated_by = Column(String(100))
