from fastapi import APIRouter, FastAPI

# 🚨 IMPORTANT: forces SQLAlchemy model registry
import app.models

from app.routes.auth import router as auth_router
from app.routes.schools import router as school_router
from app.routes.students import router as student_router
from app.routes.classes import router as class_router
from app.routes.sections import router as section_router
from app.routes.enrollments import router as enrollment_router
from app.routes.attendance import router as attendance_router
from app.routes.exams import router as exam_router
from app.routes.finance import router as finance_router
from app.routes.files import router as file_router
from app.routes.dashboard import router as dashboard_router
from app.routes.platform import router as platform_router
from app.routes.principal import router as principal_router
from app.routes.teachers import router as teachers_router
from app.routes.teacher_assignments import router as teacher_assignments_router
from app.routes import results
from app.routes.payments import router as payments_router

from app.middleware.tenant_middleware import TenantMiddleware
from app.routes.accountants import router as accountant_router
from app.database.database import engine, Base, SessionLocal

from app.seeds.role_seed import seed_roles

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import subjects

# -------------------------
# DB INIT
# -------------------------
Base.metadata.create_all(bind=engine)




# -------------------------
# RATE LIMITER
# -------------------------
limiter = Limiter(key_func=get_remote_address)


# -------------------------
# APP INIT
# -------------------------
app = FastAPI()
app.state.limiter = limiter


# -------------------------
# MIDDLEWARE (CLEANED)
# -------------------------
# -------------------------
# MIDDLEWARE
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://educoresap.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(TenantMiddleware)
# app.add_middleware(SlowAPIMiddleware)


# -------------------------
# ROUTES
# -------------------------
app.include_router(school_router)
app.include_router(student_router)
app.include_router(auth_router)
app.include_router(class_router)
app.include_router(section_router)
app.include_router(enrollment_router)
app.include_router(attendance_router)
app.include_router(exam_router)
app.include_router(finance_router)
app.include_router(file_router)
app.include_router(dashboard_router)
app.include_router(platform_router)
app.include_router(principal_router)
app.include_router(teachers_router)
app.include_router(teacher_assignments_router)
app.include_router(results.router)
app.include_router(payments_router)
app.include_router(subjects.router)
router = APIRouter(
    prefix="/accountants"
)
app.include_router(accountant_router)

# -------------------------
# STATIC FILES
# -------------------------
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# -------------------------
# ROOT
# -------------------------
@app.get("/")
def home():
    return {
        "message": "Auth System is running 🚀"
    }