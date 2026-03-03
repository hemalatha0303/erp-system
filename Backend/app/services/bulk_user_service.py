
import random
import string
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_users_from_excel(db: Session, emails: list, role: str, same_password=True):
    created = []

    common_password = generate_password() if same_password else None

    for email in emails:
        exists = db.query(User).filter(User.email == email).first()
        if exists:
            continue

        password = common_password if same_password else generate_password()

        user = User(
            email=email,
            password=hash_password(password),
            role=role,
            is_active=True
        )
        db.add(user)
        created.append({
            "email": email,
            "password": password
        })

    db.commit()
    return created
