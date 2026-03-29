from sqlalchemy.orm import Session
from app.models.notification import Notification
from sqlalchemy import or_, and_

def create_notification(db: Session, data, sender_email: str, sender_role: str):
    notification = Notification(
        title=data.title,
        message=data.message,
        target_role=data.target_role,
        batch=data.batch,
        branch=getattr(data, "branch", None),
        section=getattr(data, "section", None),
        target_email=getattr(data, "target_email", None),
        category=data.category,  # Save Category
        priority=data.priority,  # Save Priority
        sender_role=sender_role,
        created_by=sender_email
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_student_notifications(db: Session, student_email: str, batch: str, branch: str = None, section: str = None):
    # Fetch generic notifications + batch/branch/section specific ones
    return db.query(Notification).filter(
        or_(
            Notification.target_role == "ALL",
            Notification.target_role == "STUDENT"
        ),
        or_(
            Notification.batch == batch,
            Notification.batch == None
        ),
        or_(
            Notification.branch == branch,
            Notification.branch == None
        ),
        or_(
            Notification.section == section,
            Notification.section == None
        ),
        or_(
            Notification.target_email == None,
            Notification.target_email == student_email
        )
    ).order_by(Notification.created_at.desc()).all()

def get_faculty_notifications(db: Session, faculty_email: str, branch: str = None):
    return db.query(Notification).filter(
        or_(
            and_(
                or_(
                    Notification.target_role == "ALL",
                    Notification.target_role == "FACULTY"
                ),
                or_(
                    Notification.branch == branch,
                    Notification.branch == None
                ),
                or_(
                    Notification.target_email == None,
                    Notification.target_email == faculty_email
                )
            ),
            and_(
                Notification.sender_role == "FACULTY",
                Notification.created_by == faculty_email
            )
        )
    ).order_by(Notification.created_at.desc()).all()

def get_hod_notifications(db: Session, hod_email: str):
    return db.query(Notification).filter(
        or_(
            Notification.target_role == "ALL",
            Notification.target_role == "HOD"
        ),
        or_(
            Notification.target_email == None,
            Notification.target_email == hod_email
        )
    ).order_by(Notification.created_at.desc()).all()
