from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

from fastapi import (
    Depends,
    HTTPException
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from app.models.school_model import School
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user_model import User
from app.models.user_role_model import UserRole
from app.models.role_model import Role


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

security = HTTPBearer()


# -------------------------
# TOKEN CREATION
# -------------------------
def create_access_token(data: dict):

    to_encode = data.copy()

    to_encode.update({
        "exp":
        datetime.utcnow()
        + timedelta(minutes=15)
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(data: dict):

    to_encode = data.copy()

    to_encode.update({
        "exp":
        datetime.utcnow()
        + timedelta(days=7)
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# -------------------------
# DECODE TOKEN
# -------------------------
def decode_token(token: str):

    try:

        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except JWTError:

        return None


# -------------------------
# RBAC ROLE LOOKUP
# -------------------------
def get_user_role(
    db: Session,
    user_id: int
):

    role_link = db.query(
        UserRole
    ).filter(
        UserRole.user_id == user_id
    ).first()

    if not role_link:
        return None

    role = db.query(
        Role
    ).filter(
        Role.id == role_link.role_id
    ).first()

    if not role:
        return None

    return role.name


# -------------------------
# CURRENT USER
# -------------------------
def get_current_user(

    credentials:
    HTTPAuthorizationCredentials =
    Depends(security),

    db: Session = Depends(get_db)

):

    token = credentials.credentials

    payload = decode_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # RBAC role lookup
    role = get_user_role(
        db,
        user.id
    )

    if role:
        user.role = role

    # Platform admin bypass
    if role != "platform_admin":

        if user.school_id is None:

            raise HTTPException(
                status_code=403,
                detail="School missing"
            )

        school = db.query(School).filter(
            School.id == user.school_id
        ).first()

        if not school:

            raise HTTPException(
                status_code=403,
                detail="School not found"
            )

        if not school.is_active:

            raise HTTPException(
                status_code=403,
                detail="School has been deactivated by Platform Admin"
            )

    return user