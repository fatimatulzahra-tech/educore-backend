from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)
from app.models.enrollment_model import Enrollment
from sqlalchemy.orm import Session
from app.core.settings import CURRENT_ACADEMIC_YEAR
from app.core.settings import DEFAULT_USER_PASSWORD
from app.database.database import get_db

from app.models.student_model import Student

from app.schemas.student_schema import (
    StudentCreate
)
from app.models.user_model import User
from app.models.role_model import Role
from app.models.user_role_model import UserRole

from app.utils.hash import hash_password
import secrets
from app.dependencies.permission_dependencies import (
    require_permission
)

from app.utils.audit import (
    create_audit_log
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# -------------------------
# SERIALIZATION HELPER
# -------------------------
def serialize_student(student: Student) -> dict:
    return {
        "id": student.id,
        "school_id": student.school_id,
        "user_id": student.user_id,
        "class_id": student.class_id,
        "section_id": student.section_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "admission_number": student.admission_number,
        "admission_date": student.admission_date,
        "gender": student.gender,
        "date_of_birth": student.date_of_birth,
        "parent_name": student.parent_name,
        "parent_phone": student.parent_phone,
        "email": student.email,
        "phone": student.phone,
        "address": student.address,
    }


# -------------------------
# CREATE STUDENT
# -------------------------
@router.post("/")
def create_student(

    data: StudentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    existing_student = db.query(Student).filter(

        Student.admission_number == data.admission_number,

        Student.school_id == current_user.school_id

    ).first()

    if existing_student:

        raise HTTPException(
            status_code=400,
            detail="Admission number already exists"
        )

    existing_user = db.query(User).filter(

        User.email == data.email

    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    temporary_password = secrets.token_hex(4)

    # -------------------------
    # CREATE USER
    # -------------------------

    user = User(

        school_id=current_user.school_id,

        email=data.email,

        hashed_password=hash_password(temporary_password),

        role="student",

        is_verified=True,

        is_first_login=True,

    )

    db.add(user)
    db.flush()

    # -------------------------
    # ASSIGN ROLE
    # -------------------------

    role = db.query(Role).filter(

        Role.name == "student"

    ).first()

    if not role:

        raise HTTPException(
            status_code=500,
            detail="Student role not found"
        )

    db.add(

        UserRole(

            user_id=user.id,

            role_id=role.id

        )

    )

    # -------------------------
    # CREATE STUDENT
    # -------------------------

    student = Student(
    school_id=current_user.school_id,
    user_id=user.id,
    class_id=data.class_id,
    section_id=data.section_id,

    first_name=data.first_name,
    last_name=data.last_name,

    admission_number=data.admission_number,
    admission_date=data.admission_date,

    gender=data.gender,

    date_of_birth=data.date_of_birth,

    parent_name=data.parent_name,
    parent_phone=data.parent_phone,

    email=data.email,
    phone=data.phone,
    address=data.address
)
    db.add(student)
    db.flush()

    # -------------------------
    # CREATE ENROLLMENT
    # -------------------------

    enrollment = Enrollment(

        school_id=current_user.school_id,

        student_id=student.id,

        class_id=data.class_id,

        section_id=data.section_id,

        academic_year=CURRENT_ACADEMIC_YEAR

    )

    db.add(enrollment)

    db.commit()

    db.refresh(student)

    create_audit_log(

        db=db,

        user_id=current_user.id,

        school_id=current_user.school_id,

        action="CREATE",

        entity="Student",

        entity_id=student.id

    )

    return {

        "message": "Student created successfully",

        "student": serialize_student(student),

        "login": {

            "email": data.email,

            "temporary_password": temporary_password

        }

    }


# -------------------------
# UPDATE STUDENT
# -------------------------
@router.put("/{student_id}")
def update_student(

    student_id: int,

    data: StudentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    student = db.query(Student).filter(

        Student.id == student_id,

        Student.school_id == current_user.school_id

    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.class_id = data.class_id
    student.section_id = data.section_id
    student.first_name = data.first_name
    student.last_name = data.last_name
    student.admission_number = data.admission_number
    student.gender = data.gender
    student.email = data.email
    student.phone = data.phone
    student.address = data.address
    student.admission_date = data.admission_date

    student.date_of_birth = data.date_of_birth

    student.parent_name = data.parent_name

    student.parent_phone = data.parent_phone

    db.commit()

    db.refresh(student)

    return {
        "message": "Student updated successfully",
        "student": serialize_student(student)
    }


# -------------------------
# GET STUDENTS
# -------------------------
@router.get("/")
def get_students(

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    gender: str | None = None,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(Student)

    query = apply_tenant_filter(

        query=query,

        model=Student,

        current_user=current_user

    )

    if gender:

        query = query.filter(
            Student.gender == gender
        )

    total = query.count()

    skip = (page - 1) * limit

    students = query.offset(
        skip
    ).limit(
        limit
    ).all()

    return {

        "page": page,

        "limit": limit,

        "total": total,

        "data": [serialize_student(s) for s in students]

    }


# -------------------------
# GET STUDENTS BY CLASS & SECTION (FOR TEACHER)
# -------------------------
@router.get("/teacher")
def teacher_students(

    class_id: int,

    section_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(

        require_permission(

            "view_students"

        )

    )

):

    query = db.query(Student)

    query = apply_tenant_filter(

        query=query,

        model=Student,

        current_user=current_user

    )

    query = query.filter(

        Student.class_id == class_id,

        Student.section_id == section_id

    )

    students = query.all()

    return [serialize_student(s) for s in students]