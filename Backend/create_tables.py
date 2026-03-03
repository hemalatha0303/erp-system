from app.core.database import engine, Base
from app.models.user import User
from app.models.student import Student
from app.models.academic import Academic
from app.models.faculty import Faculty
from app.models.payment import Payment
from app.models.fee_structure import FeeStructure
from app.models.internal_marks import InternalMarks
from app.models.external_marks import ExternalMarks
from app.models.semester_result import SemesterResult
from app.models.subject import Subject
from app.models.attendance_record import AttendanceRecord
from app.models.attendance_session import AttendanceSession
from app.models.hostel_room import HostelRoom
from app.models.hostel_allocation import HostelAllocation
from app.models.library_books import LibraryBooks
from app.models.library_issue import LibraryIssue
from app.models.timetable import TimeTable
from app.models.hod import HODProfile
from app.models.admin import AdminProfile
from app.models.notification import Notification
from app.models.alert import Alert
Base.metadata.create_all(bind=engine)
print("Tables created successfully")