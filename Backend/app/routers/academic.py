from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.services.academic_service import insert_academics_bulk
from app.utils.excel_reader import extract_academic_rows
from app.models.academic import Academic   
from app.schemas.academic import AcademicResponse

router = APIRouter(prefix="/academic", tags=["Academics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/my", response_model=list[AcademicResponse])
def view_my_academics(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403)

    return db.query(Academic).filter(
        Academic.user_email == user["sub"]
    ).all()
