
import os

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey12345678912345678912345678")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Hema7254@127.0.0.1:3306/erp_db")