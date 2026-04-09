import logging
import time
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

engine_options = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_database(max_retries: int = 30, delay_seconds: int = 2) -> None:
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection established on attempt %s", attempt)
            return
        except Exception as exc:
            logger.warning(
                "Database not ready yet (attempt %s/%s): %s",
                attempt,
                max_retries,
                exc,
            )
            time.sleep(delay_seconds)

    raise RuntimeError("Database did not become ready in time.")


def check_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def init_db() -> None:
    wait_for_database()

    from app.models.academic import Academic
    from app.models.admin import AdminProfile
    from app.models.alert import Alert
    from app.models.attendance_record import AttendanceRecord
    from app.models.attendance_session import AttendanceSession
    from app.models.external_marks import ExternalMarks
    from app.models.faculty import Faculty
    from app.models.fee_structure import FeeStructure
    from app.models.hod import HODProfile
    from app.models.hostel_allocation import HostelAllocation
    from app.models.hostel_room import HostelRoom
    from app.models.internal_marks import InternalMarks
    from app.models.library_books import LibraryBooks
    from app.models.library_issue import LibraryIssue
    from app.models.notification import Notification
    from app.models.payment import Payment
    from app.models.semester_result import SemesterResult
    from app.models.student import Student
    from app.models.subject import Subject
    from app.models.timetable import TimeTable
    from app.models.user import User

    _ = (
        Academic,
        AdminProfile,
        Alert,
        AttendanceRecord,
        AttendanceSession,
        ExternalMarks,
        Faculty,
        FeeStructure,
        HODProfile,
        HostelAllocation,
        HostelRoom,
        InternalMarks,
        LibraryBooks,
        LibraryIssue,
        Notification,
        Payment,
        SemesterResult,
        Student,
        Subject,
        TimeTable,
        User,
    )

    Base.metadata.create_all(bind=engine)
