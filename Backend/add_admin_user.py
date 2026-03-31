"""
Script to add admin user to Railway MySQL database
Run this once to create the first admin account
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.admin import AdminProfile
from app.core.security import hash_password

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@127.0.0.1:3306/erp_db"
)

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
            password=hashed_pwd,
            role="ADMIN",
            is_active=True
        )
        db.add(user)
        
        # Create admin profile
        admin = AdminProfile(
            email=email,
            name=name,
            mobile_no="",
            designation=""
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
    print("   Role: ADMIN")
