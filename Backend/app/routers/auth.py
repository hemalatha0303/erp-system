
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import (
    SignupRequest, LoginRequest, TokenResponse, ChangePasswordRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.services.auth_service import (
    signup, login, change_password, request_password_reset,
    verify_reset_token_and_update_password
)
from app.core.database import SessionLocal
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
    user, message = signup(db, req.email, req.password, req.role, req.personal_email)
    if not user:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/login", response_model=TokenResponse)
def signin(req: LoginRequest, db: Session = Depends(get_db)):
    # If role is provided, validate it matches the user's role
    token = login(db, req.email, req.password, role=req.role)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials or role mismatch")
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


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset. Sends reset link to user's personal email.
    """
    success, message = request_password_reset(db, req.email)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using the reset token sent via email.
    """
    success, message = verify_reset_token_and_update_password(
        db, req.email, req.reset_token, req.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}

