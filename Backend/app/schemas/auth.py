
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SignupRequest(BaseModel):
    email: str = Field(..., description="University email (@vvit.net)")
    password: str = Field(..., description="Password (min 6 characters)")
    personal_email: str = Field(..., description="Personal email for password recovery")
    role: str = Field(..., description="User role: STUDENT, FACULTY, HOD, or ADMIN")

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str = None  # Optional role for role-based verification

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_token: str
    new_password: str
