from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all routers
from app.routers.auth import router as auth_router
from app.routers.student import router as student_router
from app.routers.student_grades import router as student_grades_router
from app.routers.faculty import router as faculty_router
from app.routers.academic import router as academic_router
from app.routers.admin_accounts import router as admin_accounts_router
from app.routers.payment import router as payment_router
from app.routers.admin import router as admin_router
from app.routers.library import router as library_router
from app.routers.hod import router as hod_router
from app.routers.ai_route import router as ai_router

# Create FastAPI app
app = FastAPI(title="ERP Student Management System", version="1.0.0")

# Setup base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount(
    "/uploads",
    StaticFiles(directory=os.path.join(BASE_DIR, "..", "uploads")),
    name="uploads",
)

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:8080,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(student_grades_router)
app.include_router(faculty_router)
app.include_router(academic_router)
app.include_router(admin_accounts_router)   
app.include_router(payment_router)
app.include_router(admin_router)
app.include_router(library_router)
app.include_router(hod_router)
app.include_router(ai_router)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ERP Backend"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "ERP Student Management System", "version": "1.0.0"}