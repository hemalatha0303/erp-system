from sqlalchemy.orm import Session
from app.models.notification import Notification
from sqlalchemy import or_

def create_notification(db: Session, data, admin_email: str):
    notification = Notification(
        title=data.title,
        message=data.message,
        target_role=data.target_role,
        batch=data.batch,
        category=data.category,  # Save Category
        priority=data.priority,  # Save Priority
        created_by=admin_email
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_student_notifications(db: Session, student_email: str, batch: str):
    # Fetch generic notifications + batch specific ones
    return db.query(Notification).filter(
        or_(
            Notification.target_role == "ALL",
            Notification.target_role == "STUDENT"
        ),
        or_(
            Notification.batch == batch,
            Notification.batch == None
        )
    ).order_by(Notification.created_at.desc()).all()