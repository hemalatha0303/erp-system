from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.utils.excel_reader import extract_emails
from app.services.bulk_user_service import create_users_from_excel
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/admin/accounts", tags=["Admin Accounts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup-users")
def upload_users(
    role: str = Query(..., description="STUDENT or FACULTY"),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    emails = extract_emails(file.file)
    created_users = create_users_from_excel(db, emails, role)

    return {
        "count": len(created_users),
        "credentials": created_users
    }
