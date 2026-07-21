from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.accountant_model import Accountant
from app.models.user_model import User
from app.models.role_model import Role
from app.models.user_role_model import UserRole
from app.core.settings import DEFAULT_USER_PASSWORD
from app.schemas.accountant_schema import AccountantCreate

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter

from app.utils.hash import hash_password

import secrets

router = APIRouter(
    prefix="/accountants",
    tags=["Accountants"]
)


@router.post("/")
def create_accountant(

    data: AccountantCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
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

        hashed_password=hash_password(DEFAULT_USER_PASSWORD),

        role="accountant",

        is_verified=True,

        is_first_login=True

    )

    db.add(user)
    db.flush()

    # -------------------------
    # ASSIGN ROLE
    # -------------------------

    role = db.query(Role).filter(

        Role.name == "accountant"

    ).first()

    if not role:

        raise HTTPException(
            status_code=500,
            detail="Accountant role missing"
        )

    db.add(

        UserRole(

            user_id=user.id,

            role_id=role.id

        )

    )

    # -------------------------
    # CREATE ACCOUNTANT
    # -------------------------

    accountant = Accountant(

        school_id=current_user.school_id,

        user_id=user.id,

        first_name=data.first_name,

        last_name=data.last_name,

        email=data.email,

        phone=data.phone

    )

    db.add(accountant)

    db.commit()

    db.refresh(accountant)

    return {

        "message":
        "Accountant created successfully",

        "accountant":
        accountant,

        "login": {

            "email":
            data.email,

            "temporary_password": DEFAULT_USER_PASSWORD

        }

    }
@router.get("/")
def get_accountants(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    query = db.query(Accountant)

    query = apply_tenant_filter(
        query=query,
        model=Accountant,
        current_user=current_user
    )

    accountants = query.all()

    result = []

    for accountant in accountants:

        user = db.query(User).filter(
            User.email == accountant.email
        ).first()

        result.append({
            "id": accountant.id,
            "user_id": user.id if user else None,
            "first_name": accountant.first_name,
            "last_name": accountant.last_name,
            "email": accountant.email,
            "phone": accountant.phone
        })

    return result



@router.delete("/{accountant_id}")
def delete_accountant(

    accountant_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    accountant = db.query(Accountant).filter(

        Accountant.id == accountant_id,

        Accountant.school_id == current_user.school_id

    ).first()

    if not accountant:

        raise HTTPException(
            status_code=404,
            detail="Accountant not found"
        )

    user = db.query(User).filter(

        User.email == accountant.email

    ).first()

    if user:

        db.query(UserRole).filter(

            UserRole.user_id == user.id

        ).delete()

        db.delete(user)

    db.delete(accountant)

    db.commit()

    return {

        "message":
        "Accountant deleted successfully"

    }

@router.put("/{accountant_id}")
def update_accountant(
    accountant_id: int,
    data: AccountantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_finance")
    )
):

    accountant = db.query(Accountant).filter(
        Accountant.id == accountant_id,
        Accountant.school_id == current_user.school_id
    ).first()

    if not accountant:
        raise HTTPException(
            status_code=404,
            detail="Accountant not found"
        )

    accountant.first_name = data.first_name
    accountant.last_name = data.last_name
    accountant.phone = data.phone

    db.commit()

    return {
        "message": "Accountant updated successfully"
    }