from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.core.security import hash_password, verify_password, create_jwt
from app.utils.validators import validate_vvit_and_format
from app.services.email_service import send_password_reset_email
from app.core.config import PASSWORD_RESET_BASE_URL
import secrets
from datetime import datetime, timedelta

def signup(db: Session, email: str, password: str, role: str, personal_email: str):
    # Validate email format and @vvit.net domain
    if not validate_vvit_and_format(email):
        return None, "Email must end with @vvit.net"
    
    # Check if personal_email is provided
    if not personal_email or personal_email.strip() == "":
        return None, "Personal email is required for password recovery"
    
    normalized_email = email.strip().lower()
    normalized_role = (role or "").strip().upper()

    if normalized_role not in {"STUDENT", "FACULTY", "HOD", "ADMIN"}:
        return None, "Invalid role. Use STUDENT, FACULTY, HOD, or ADMIN"

    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        return None, "User already exists. Please login instead."

    user = User(
        email=normalized_email,
        password=hash_password(password),
        role=normalized_role,
        personal_email=personal_email
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        if normalized_role == "HOD":
            from app.models.hod import HODProfile
            hod_profile = HODProfile(email=normalized_email)
            db.add(hod_profile)
            db.commit()
            db.refresh(hod_profile)
        if normalized_role == "ADMIN":
            from app.models.admin import AdminProfile
            admin_profile = AdminProfile(email=normalized_email)
            db.add(admin_profile)
            db.commit()
            db.refresh(admin_profile)
        return user, "User created successfully"
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Signup DB error: {e}")
        return None, "Could not create user. Check email uniqueness and role data."

def login(db: Session, email: str, password: str, role: str = None):
    """
    Login with email, password and optional role verification.
    
    Args:
        db: Database session
        email: User email
        password: User password
        role: Optional role to verify against (STUDENT, FACULTY, HOD, ADMIN)
    
    Returns:
        Token if valid credentials, None otherwise
    """
    # Validate email format
    if not validate_vvit_and_format(email):
        return None
    
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.password):
        return None
    
    # Check if role matches (if role is specified)
    if role and user.role != role.upper():
        return None
    
    token = create_jwt(user.email, user.role)
    return token

def change_password(db: Session, email: str, old_password: str, new_password: str):
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        return False, "User not found"

    if not verify_password(old_password, user.password):
        return False, "Old password is incorrect"

    user.password = hash_password(new_password)
    db.commit()
    return True, "Password updated successfully"


def request_password_reset(db: Session, email: str):
    """
    Generate a password reset token and send email to user's personal email.
    
    Args:
        db: Database session
        email: User's vvit.net email
        
    Returns:
        Tuple of (success, message)
    """
    if not validate_vvit_and_format(email):
        return False, "Invalid email format. Must end with @vvit.net"
    
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        return False, "Email not found in system"
    
    # User must have a personal email set
    if not user.personal_email:
        return False, "Personal email not set in your profile. Please contact admin."
    
    # Generate a secure reset token
    reset_token = secrets.token_urlsafe(32)
    reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
    
    # Store token and expiry in user record
    user.reset_token = reset_token
    user.reset_token_expiry = reset_token_expiry
    db.commit()
    
    # Create reset link
    reset_link = f"{PASSWORD_RESET_BASE_URL}?token={reset_token}&email={email}"
    
    # Send email to personal email
    email_sent = send_password_reset_email(
        recipient_email=user.personal_email,
        reset_link=reset_link,
        user_name=email.split("@")[0]
    )
    
    if email_sent:
        return True, f"Password reset link sent to {user.personal_email}"
    else:
        return False, "Failed to send reset email. Please try again."


def verify_reset_token_and_update_password(db: Session, email: str, reset_token: str, new_password: str):
    """
    Verify reset token and update password.
    
    Args:
        db: Database session
        email: User email
        reset_token: The reset token provided
        new_password: New password to set
        
    Returns:
        Tuple of (success, message)
    """
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        return False, "User not found"
    
    # Verify reset token
    if not user.reset_token or user.reset_token != reset_token:
        return False, "Invalid reset token"
    
    # Check if token has expired
    if user.reset_token_expiry and datetime.utcnow() > user.reset_token_expiry:
        return False, "Reset token has expired. Please request a new one."
    
    # Update password
    user.password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    
    return True, "Password reset successfully. You can now login with your new password."


