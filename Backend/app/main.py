from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.student import router as student_router
from app.routers.faculty import router as faculty_router
from app.routers.academic import router as academic_router
from app.routers.admin_accounts import router as admin_accounts_router
from app.routers.payment import router as payment_router
from app.routers.admin import router as admin_router
from app.routers.library import router as library_router
from app.routers.hod import router as hod_router
from app.routers.ai_route import router as ai_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
app = FastAPI(title="ERP Student Management System")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/uploads",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "uploads")),
    name="uploads",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(student_router)
app.include_router(faculty_router)
app.include_router(academic_router)
app.include_router(admin_accounts_router)   
app.include_router(payment_router)
app.include_router(admin_router)
app.include_router(library_router)
app.include_router(hod_router)
app.include_router(ai_router)