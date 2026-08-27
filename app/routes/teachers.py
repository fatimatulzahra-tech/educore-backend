from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.teacher_model import Teacher
from app.models.user_model import User
from app.models.role_model import Role
from app.models.user_role_model import UserRole
from app.core.settings import DEFAULT_USER_PASSWORD
from app.schemas.teacher_schema import TeacherCreate
from app.utils.hash import hash_password
from app.dependencies.permission_dependencies import require_permission
from app.core.query import apply_tenant_filter

import secrets

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

# -------------------------
# CREATE TEACHER
# -------------------------
@router.post("/")
def create_teacher(
    data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("manage_students"))
):

    # -----------------------------
    # CHECK EXISTING USER
    # -----------------------------
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    temp_password = None

    # -----------------------------
    # CREATE USER IF NOT EXISTS
    # -----------------------------
    if not user:

        temp_password = secrets.token_urlsafe(8)

        user = User(
            email=data.email,
            hashed_password=hash_password(temp_password),
            school_id=current_user.school_id,
            role="teacher",
            is_verified=True,
            is_first_login=True
        )

        db.add(user)
        db.flush()

        role = db.query(Role).filter(
            Role.name == "teacher",
            Role.school_id == current_user.school_id
        ).first()

        if role:
            db.add(
                UserRole(
                    user_id=user.id,
                    role_id=role.id
                )
            )

    # -----------------------------
    # CHECK EXISTING TEACHER (UPDATED FIX)
    # -----------------------------
    existing_teacher = db.query(Teacher).filter(
        Teacher.user_id == user.id,
        Teacher.school_id == current_user.school_id
    ).first()

    if existing_teacher:
        return {
            "message": "Teacher already exists"
        }

    # -----------------------------
    # CREATE TEACHER PROFILE
    # -----------------------------
    teacher = Teacher(
    school_id=current_user.school_id,
    user_id=user.id,

    first_name=data.first_name,
    last_name=data.last_name,

    email=data.email,
    phone=data.phone,

    subject=data.subject,

    qualification=data.qualification,
    experience=data.experience,
    salary=data.salary,
    joining_date=data.joining_date,
    employment_type=data.employment_type,
   )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return {
        "message": "Teacher created successfully",
        "temp_password": temp_password,
        "teacher": {
            "id": teacher.id,
            "email": teacher.email,
            "user_id": teacher.user_id
        }
    }


# -------------------------
# GET TEACHERS (TENANT SAFE + USER LINKED FIX)
# -------------------------
@router.get("/")
def get_teachers(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_students")
    )
):

    query = db.query(Teacher)

    query = query.filter(
        Teacher.school_id == current_user.school_id
    )

    teachers = query.all()

    result = []

    for teacher in teachers:

        user = db.query(User).filter(
            User.id == teacher.user_id
        ).first()

        result.append({

            "id": teacher.id,

            "user_id": teacher.user_id,

            "first_name": teacher.first_name,

            "last_name": teacher.last_name,

            "email": teacher.email,

            "phone": teacher.phone,

            "subject": teacher.subject,

            "qualification": teacher.qualification,
            "experience": teacher.experience,
            "salary": teacher.salary,
            "joining_date": teacher.joining_date,
            "employment_type": teacher.employment_type,

        })

    return result












@router.get("/me")
def get_my_teacher_profile(
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("view_students"))
):

    return db.query(Teacher).filter(
        Teacher.school_id == current_user.school_id,
        Teacher.user_id == current_user.id
    ).first()

# -------------------------
# DELETE TEACHER (FIXED SAFETY)
# -------------------------
# -------------------------
# DELETE TEACHER
# -------------------------
@router.delete("/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_students")
    )
):

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.school_id == current_user.school_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    user = db.query(User).filter(
        User.id == teacher.user_id
    ).first()

    if user:
        db.query(UserRole).filter(
            UserRole.user_id == user.id
        ).delete()

        db.delete(user)

    db.delete(teacher)

    db.commit()

    return {
        "message": "Teacher deleted successfully"
    }

# -------------------------
# UPDATE TEACHER
# -------------------------
@router.put("/{teacher_id}")
def update_teacher(
    teacher_id: int,
    data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_students")
    )
):

    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id,
        Teacher.school_id == current_user.school_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    teacher.first_name = data.first_name
    teacher.last_name = data.last_name
    teacher.phone = data.phone
    teacher.subject = data.subject
    teacher.qualification = data.qualification
    teacher.experience = data.experience
    teacher.salary = data.salary
    teacher.joining_date = data.joining_date
    teacher.employment_type = data.employment_type

    db.commit()

    return {
        "message": "Teacher updated successfully"
    }