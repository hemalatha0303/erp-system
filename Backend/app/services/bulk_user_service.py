
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.faculty import Faculty
from app.models.hod import HODProfile
from app.core.security import hash_password

def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def _apply_if_value(model, attr, value):
    if value is not None and value != "":
        setattr(model, attr, value)

def _upsert_faculty_profile(db: Session, email: str, user_info: dict):
    faculty = db.query(Faculty).filter(Faculty.user_email == email).first()
    if not faculty:
        faculty = Faculty(user_email=email)
    _apply_if_value(faculty, "personal_email", user_info.get("personal_email"))
    _apply_if_value(faculty, "first_name", user_info.get("first_name"))
    _apply_if_value(faculty, "last_name", user_info.get("last_name"))
    _apply_if_value(faculty, "mobile_no", user_info.get("mobile_no"))
    _apply_if_value(faculty, "address", user_info.get("address"))
    _apply_if_value(faculty, "qualification", user_info.get("qualification"))
    _apply_if_value(faculty, "experience", user_info.get("years_of_experience"))
    _apply_if_value(faculty, "subject_code", user_info.get("subject_code"))
    _apply_if_value(faculty, "subject_name", user_info.get("subject_name"))
    _apply_if_value(faculty, "branch", user_info.get("branch"))
    db.add(faculty)

def _upsert_hod_profile(db: Session, email: str, user_info: dict):
    hod = db.query(HODProfile).filter(HODProfile.email == email).first()
    if not hod:
        hod = HODProfile(email=email)
    _apply_if_value(hod, "personal_email", user_info.get("personal_email"))
    _apply_if_value(hod, "first_name", user_info.get("first_name"))
    _apply_if_value(hod, "last_name", user_info.get("last_name"))
    _apply_if_value(hod, "mobile_no", user_info.get("mobile_no"))
    _apply_if_value(hod, "address", user_info.get("address"))
    _apply_if_value(hod, "qualification", user_info.get("qualification"))
    _apply_if_value(hod, "experience", user_info.get("years_of_experience"))
    _apply_if_value(hod, "branch", user_info.get("branch"))
    db.add(hod)

def create_users_from_excel(db: Session, user_data: list, role: str, same_password=True):
    """
    Create users from excel data.
    Only creates users with @vvit.net emails.
    Skips existing users and duplicates.
    
    Args:
        db: Database session
        user_data: List of dicts containing user information
        role: User role (STUDENT, FACULTY, HOD, ADMIN)
        same_password: If True, use same password for all users
        
    Returns:
        Dict with:
        - created: List of created user credentials
        - skipped: List of skipped users with reasons
        - errors: List of errors occurred
    """
    created = []
    skipped = []
    errors = []

    common_password = generate_password() if same_password else None
    added_emails = set()  # Track emails added in this batch

    for user_info in user_data:
        email = user_info.get("email")
        personal_email = user_info.get("personal_email")
        
        if not email:
            continue
        
        email = email.lower().strip()
        
        # Check if email ends with @vvit.net
        if not email.endswith("@vvit.net"):
            skipped.append({
                "email": email,
                "reason": "Not a @vvit.net email"
            })
            continue
        
        # Skip if already added in this batch
        if email in added_emails:
            skipped.append({
                "email": email,
                "reason": "Duplicate in current batch"
            })
            continue
        
        # Check if user already exists in database
        try:
            exists = db.query(User).filter(User.email == email).first()
            if exists:
                if personal_email and not exists.personal_email:
                    exists.personal_email = personal_email
                if role == "FACULTY":
                    _upsert_faculty_profile(db, email, user_info)
                elif role == "HOD":
                    _upsert_hod_profile(db, email, user_info)
                skipped.append({
                    "email": email,
                    "reason": "User already exists in database (profile updated)"
                })
                continue
        except Exception as e:
            errors.append({
                "email": email,
                "error": f"Database query error: {str(e)}"
            })
            continue

        password = common_password if same_password else generate_password()

        try:
            user = User(
                email=email,
                password=hash_password(password),
                role=role,
                personal_email=personal_email,
                is_active=True
            )
            db.add(user)
            added_emails.add(email)

            if role == "FACULTY":
                _upsert_faculty_profile(db, email, user_info)
            elif role == "HOD":
                _upsert_hod_profile(db, email, user_info)
            
            created.append({
                "email": email,
                "password": password,
                "personal_email": personal_email,
                "role": role
            })
        except Exception as e:
            errors.append({
                "email": email,
                "error": f"Error preparing user: {str(e)}"
            })
            continue

    # Commit all at once with error handling
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Extract the duplicate email from error message if possible
        error_msg = str(e)
        errors.append({
            "type": "IntegrityError",
            "message": "Duplicate entry or constraint violation",
            "details": error_msg[:200]  # First 200 chars of error
        })
        return {
            "created": [],
            "skipped": skipped,
            "errors": errors,
            "success": False
        }
    except Exception as e:
        db.rollback()
        errors.append({
            "type": "UnexpectedError",
            "message": str(e)[:200]
        })
        return {
            "created": [],
            "skipped": skipped,
            "errors": errors,
            "success": False
        }

    return {
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "success": len(errors) == 0
    }
