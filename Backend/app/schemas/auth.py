
from pydantic import BaseModel

class SignupRequest(BaseModel):
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
