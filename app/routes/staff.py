from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.staff_model import Staff
from app.models.user_model import User
from app.models.role_model import Role
from app.models.user_role_model import UserRole

from app.schemas.staff_schema import StaffCreate

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter

from app.utils.hash import hash_password

import secrets

router = APIRouter(
    prefix="/staff",
    tags=["Staff"]
)


def serialize_staff(staff: Staff) -> dict:
    return {
        "id": staff.id,
        "user_id": staff.user_id,
        "first_name": staff.first_name,
        "last_name": staff.last_name,
        "email": staff.email,
        "phone": staff.phone,
        "designation": staff.designation,
        "department": staff.department,
        "qualification": staff.qualification,
        "experience": staff.experience,
        "salary": staff.salary,
        "joining_date": staff.joining_date,
        "employment_type": staff.employment_type,
        "address": staff.address,
        "status": staff.status,
    }


# -------------------------
# CREATE STAFF
# -------------------------
@router.post("/")
def create_staff(

    data: StaffCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("manage_students")
    )

):

    existing = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing:
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
        role="staff",
        is_verified=True,
        is_first_login=True
    )

    db.add(user)
    db.flush()

    # -------------------------
    # ASSIGN ROLE (IF ONE EXISTS)
    # -------------------------

    role = db.query(Role).filter(
        Role.name == "staff",
        Role.school_id == current_user.school_id
    ).first()

    if role:
        db.add(
            UserRole(
                user_id=user.id,
                role_id=role.id
            )
        )

    # -------------------------
    # CREATE STAFF PROFILE
    # -------------------------

    staff = Staff(
        school_id=current_user.school_id,
        user_id=user.id,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        designation=data.designation,
        department=data.department,
        qualification=data.qualification,
        experience=data.experience,
        salary=data.salary,
        joining_date=data.joining_date,
        employment_type=data.employment_type,
        address=data.address,
        status=data.status or "Active",
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return {
        "message": "Staff created successfully",
        "staff": serialize_staff(staff),
        "login": {
            "email": data.email,
            "temporary_password": temporary_password
        }
    }


# -------------------------
# GET STAFF
# -------------------------
@router.get("/")
def get_staff(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("manage_students")
    )

):

    query = db.query(Staff)

    query = apply_tenant_filter(
        query=query,
        model=Staff,
        current_user=current_user
    )

    staff_list = query.all()

    return [serialize_staff(s) for s in staff_list]


# -------------------------
# UPDATE STAFF
# -------------------------
@router.put("/{staff_id}")
def update_staff(

    staff_id: int,

    data: StaffCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("manage_students")
    )

):

    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.school_id == current_user.school_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    staff.first_name = data.first_name
    staff.last_name = data.last_name
    staff.phone = data.phone
    staff.designation = data.designation
    staff.department = data.department
    staff.qualification = data.qualification
    staff.experience = data.experience
    staff.salary = data.salary
    staff.joining_date = data.joining_date
    staff.employment_type = data.employment_type
    staff.address = data.address
    staff.status = data.status or staff.status

    db.commit()
    db.refresh(staff)

    return {
        "message": "Staff updated successfully",
        "staff": serialize_staff(staff)
    }


# -------------------------
# DELETE STAFF
# -------------------------
@router.delete("/{staff_id}")
def delete_staff(

    staff_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("manage_students")
    )

):

    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.school_id == current_user.school_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )

    user = db.query(User).filter(
        User.id == staff.user_id
    ).first()

    if user:
        db.query(UserRole).filter(
            UserRole.user_id == user.id
        ).delete()

        db.delete(user)

    db.delete(staff)
    db.commit()

    return {
        "message": "Staff deleted successfully"
    }