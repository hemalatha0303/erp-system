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
    role: str = Query(..., description="STUDENT, FACULTY, or HOD"),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        extracted = extract_emails(file.file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    duplicate_emails = extracted.get("duplicates", [])
    if duplicate_emails:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Duplicate emails found in upload. Remove duplicates and re-upload.",
                "duplicates": duplicate_emails,
            },
        )

    result = create_users_from_excel(db, extracted.get("users", []), role)

    return {
        "success": result.get("success", False),
        "created_count": len(result.get("created", [])),
        "skipped_count": len(result.get("skipped", [])),
        "error_count": len(result.get("errors", [])),
        "created_users": result.get("created", []),
        "skipped_users": result.get("skipped", []),
        "errors": result.get("errors", [])
    }
