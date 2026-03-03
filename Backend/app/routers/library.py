from http.client import HTTPException
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.library import IssueBooksRequest, ReturnBooksRequest
from app.services.library_service import *
from app.models.library_books import LibraryBooks
router = APIRouter(prefix="/library", tags=["Library"])


@router.get("/books")
def get_library_catalog(
    search: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(LibraryBooks)
    if search:
        query = query.filter(LibraryBooks.title.contains(search))
    return query.limit(50).all()

@router.post("/books/upload")
def upload_books(
    file: UploadFile,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    upload_books_excel(db, file)
    return {"message": "Books uploaded successfully"}

@router.post("/issue")
def issue_books(
    req: IssueBooksRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403)

    issue_books_to_student(db, req)
    return {"message": "Books issued successfully"}

@router.post("/return")
def return_library_books(
    req: ReturnBooksRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admin allowed")

    return return_books(db, req, user["sub"])


@router.get("/pending")
def pending_books(
    srno: str,
    semester: int,
    db: Session = Depends(get_db)
):
    return get_pending_books(db, srno, semester)
@router.get("/student/books")
def get_student_books(
    semester: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students allowed")

    return get_student_library_books(db, user["sub"], semester)