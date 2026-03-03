
from sqlalchemy.orm import Session
from app.models.hod import HODProfile

def get_hod_profile(db: Session, email: str):
    return db.query(HODProfile).filter(HODProfile.email == email).first()

def update_hod_profile(db: Session, email: str, data):
    hod = get_hod_profile(db, email)
    if not hod:
        return None

    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(hod, key, value) 

    db.commit()
    db.refresh(hod)
    return hod
