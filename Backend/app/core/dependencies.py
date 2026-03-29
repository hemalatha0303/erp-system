from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

security = HTTPBearer()
from jose import jwt, JWTError
from app.core.config import JWT_SECRET, JWT_ALGORITHM   
SECRET_KEY = JWT_SECRET
ALGORITHM = JWT_ALGORITHM
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
from jose import jwt, JWTError
from app.core.config import JWT_SECRET, JWT_ALGORITHM

security = HTTPBearer()