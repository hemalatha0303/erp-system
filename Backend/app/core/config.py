
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey12345678912345678912345678")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Hema7254@127.0.0.1:3306/erp_db")

# SMTP Configuration for Email Service
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")

# Password Reset Link Base URL
PASSWORD_RESET_BASE_URL = os.getenv("PASSWORD_RESET_BASE_URL", "http://localhost:3000/reset-password.html") 



# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

if not JWT_SECRET or JWT_SECRET == "your-default-secret-key":
    import warnings
    warnings.warn("⚠️ JWT_SECRET not set! Using default value - NOT SECURE FOR PRODUCTION")