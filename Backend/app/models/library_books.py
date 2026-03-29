from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.core.database import Base
class LibraryBooks(Base):
    __tablename__ = "library_books"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    available_copies = Column(Integer, default=1)

    