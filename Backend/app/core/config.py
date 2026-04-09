import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

JWT_SECRET = (
    os.getenv("JWT_SECRET")
    or os.getenv("SECRET_KEY")
    or "supersecretkey12345678912345678912345678"
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@127.0.0.1:3306/erp_db",
)

# SMTP Configuration for Email Service
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", os.getenv("SENDER_EMAIL", "your_email@gmail.com"))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USERNAME)

# Password Reset Link Base URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost").rstrip("/")
PASSWORD_RESET_BASE_URL = os.getenv(
    "PASSWORD_RESET_BASE_URL",
    f"{FRONTEND_URL}/reset-password.html",
)
