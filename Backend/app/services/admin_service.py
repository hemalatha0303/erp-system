from sqlalchemy.orm import Session
from app.models.admin import AdminProfile
from app.services.hod_service import get_hod_profile
def get_admin_profile(db: Session, email: str):
    return db.query(AdminProfile).filter(AdminProfile.email == email).first()

def update_admin_profile(db: Session, email: str, data):
    admin = get_admin_profile(db, email)
    if not admin:
        return None

    for key, value in data.dict().items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)
    return admin
def view_hod_profile(db: Session, email: str):
    return get_hod_profile(db, email)