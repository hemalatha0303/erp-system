
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.services.auth_service import signup, login
from app.core.database import SessionLocal
from app.schemas.auth import ChangePasswordRequest
from app.services.auth_service import change_password
from app.core.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def register(req: SignupRequest, db: Session = Depends(get_db)):
    signup(db, req.email, req.password, req.role)
    return {"message": "User created successfully"}

@router.post("/login", response_model=TokenResponse)
def signin(req: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, req.email, req.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}

@router.post("/change-password")
def change_user_password(
    req: ChangePasswordRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = user["sub"]  

    success, message = change_password(
        db,
        email=email,
        old_password=req.old_password,
        new_password=req.new_password
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}
