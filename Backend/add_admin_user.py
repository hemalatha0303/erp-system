"""
Script to add admin user to Railway MySQL database
Run this once to create the first admin account
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.models.admin import AdminProfile
from app.core.database import Base

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@127.0.0.1:3306/erp_db"
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_admin_user(email: str, password: str, name: str = "Admin"):
    """Create admin user in database"""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as db:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User {email} already exists!")
            return False
        
        # Create user
        hashed_pwd = hash_password(password)
        user = User(
            email=email,
            password_hash=hashed_pwd,
            role="ADMIN",
            is_active=True
        )
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create admin profile
        admin = AdminProfile(
            uid=user.id,
            first_name=name.split()[0],
            last_name=name.split()[1] if len(name.split()) > 1 else "",
            email=email,
            personal_email=email,
            mobile_no="",
            address="",
            qualification="",
            experience="",
            department=""
        )
        db.add(admin)
        db.commit()
        
        print(f"✅ Admin created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: ADMIN")
        return True

if __name__ == "__main__":
    # Create admin user
    print("🔐 Creating Admin User...")
    create_admin_user(
        email="admin@vvit.net",
        password="Admin@123",
        name="System Admin"
    )
    
    print("\n📝 Now you can login with these credentials:")
    print("   Email: admin@vvit.net")
    print("   Password: Admin@123")
    print("   Role: Admin")
