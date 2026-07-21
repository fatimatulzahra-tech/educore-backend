from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException
)
import secrets
from app.schemas.admin_reset_password_schema import (
    AdminResetPasswordRequest
)

from app.dependencies.permission_dependencies import (
    require_permission
)
from app.models.role_model import Role
from app.models.user_role_model import UserRole

from app.utils.hash import hash_password

from app.dependencies.permission_dependencies import (
    require_permission
)
from app.models.school_model import School
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.utils.auth_rules import requires_password_flow
from app.database.database import get_db
from app.schemas.change_password_schema import (
    ChangePasswordRequest
)
from app.models.user_model import User
from app.models.refresh_token_model import RefreshToken

from app.models.role_model import Role
from app.models.user_role_model import UserRole

from app.schemas.auth_schema import (
    LoginRequest,
    SignupRequest,
    LogoutRequest,
    RefreshTokenRequest
)

from app.utils.hash import (
    hash_password,
    verify_password
)

from app.utils.token_generator import generate_token

from app.utils.jwt import (
    get_current_user,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)


from app.utils.role_checker import require_role



router = APIRouter(prefix="/auth")

limiter = Limiter(
    key_func=get_remote_address
)


# -------------------------
# SIGNUP
# -------------------------
@router.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    verification_token = generate_token()

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        verification_token=verification_token
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User created successfully",
        "verification_token": verification_token
    }


# -------------------------
# VERIFY EMAIL
# -------------------------
@router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.verification_token == token
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return {
        "message": "Email verified successfully"
    }


# -------------------------
# LOGIN (FIXED RBAC VERSION)
# -------------------------
@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify email first")

    # -------------------------
    # RBAC ROLE RESOLUTION (SOURCE OF TRUTH)
    # -------------------------
    role_obj = db.query(Role).join(UserRole).filter(
        UserRole.user_id == user.id
    ).first()

    role_name = role_obj.name if role_obj else "user"



    # -------------------------
# SCHOOL STATUS CHECK
# -------------------------
    if role_name != "platform_admin":

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

# -------------------------
# FIRST LOGIN PASSWORD FLOW
# -------------------------
    password_flow_required = requires_password_flow(
    role_name
    )

    access_token = create_access_token({
    "sub": user.email,
    "user_id": user.id,
    "role": role_name,
    "school_id": user.school_id
    })

    refresh_token = create_refresh_token({
    "sub": user.email,
    "user_id": user.id
    })
    db_refresh = RefreshToken(
        token=refresh_token,
        user_id=user.id
    )

    db.add(db_refresh)
    db.commit()
# -------------------------
# FORCE PASSWORD CHANGE
# -------------------------
    

    if (

    password_flow_required

    and user.is_first_login

):

      return {

        "access_token": access_token,

        "refresh_token": refresh_token,

        "require_password_change": True,

        "role": role_name,

        "school_id": user.school_id,

        "user_id": user.id

    }

    return {

    "access_token": access_token,

    "refresh_token": refresh_token,

    "require_password_change": False,

    "role": role_name,

    "school_id": user.school_id,

    "user_id": user.id

}



    


# -------------------------
# CURRENT USER (/me FIXED)
# -------------------------
@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    role_obj = db.query(Role).join(UserRole).filter(
        UserRole.user_id == current_user.id
    ).first()

    role_name = role_obj.name if role_obj else "user"

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": role_name,
        "school_id": current_user.school_id
    }


# -------------------------
# REFRESH TOKEN
# -------------------------
@router.post("/refresh")
def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    stored = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token
    ).first()

    if not stored:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    try:
        payload = jwt.decode(
            data.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    role_obj = db.query(Role).join(UserRole).filter(
        UserRole.user_id == user.id
    ).first()

    role_name = role_obj.name if role_obj else "user"

    access_token = create_access_token({
        "sub": user.email,
        "user_id": user.id,
        "role": role_name,
        "school_id": user.school_id
    })

    return {
        "access_token": access_token
    }


# -------------------------
# LOGOUT
# -------------------------
@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):

    token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token
    ).first()

    if token:
        db.delete(token)
        db.commit()

    return {
        "message": "Logged out successfully"
    }


# -------------------------
# ADMIN TEST ROUTE
# -------------------------
@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(get_current_user)
):

    require_role("admin")(current_user)

    return {
        "message": "Welcome Admin"
    }

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    current_user.hashed_password = hash_password(
        data.new_password
    )

    current_user.is_first_login = False

    db.commit()

    return {
        "message": "Password changed successfully"
    }

@router.post("/reset-user-password/{user_id}")
def reset_user_password(

    user_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    role_obj = db.query(Role).join(
        UserRole
    ).filter(
        UserRole.user_id == user.id
    ).first()

    role = role_obj.name if role_obj else None

    if role in [
        "platform_admin",
        "principal"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Cannot reset this user"
        )

    if user.school_id != current_user.school_id:

        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )

    DEFAULT_PASSWORD = "Saap@1234"

    user.hashed_password = hash_password(
        DEFAULT_PASSWORD
    )

    user.is_first_login = True

    db.commit()

    return {

        "message":
        "Password reset successful",

        "temporary_password":
        DEFAULT_PASSWORD

    }

# -------------------------
# PRINCIPAL PASSWORD RESET
# -------------------------
@router.post("/admin-reset-password")
def admin_reset_password(

    data: AdminResetPasswordRequest,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )
):

    user = db.query(User).filter(

        User.id == data.user_id,

        User.school_id ==
        current_user.school_id

    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    default_password = "EduCore@123"

    user.hashed_password = hash_password(
        default_password
    )

    user.is_first_login = True

    db.commit()

    return {

        "message":
        "Password reset successfully",

        "temporary_password":
        default_password
    }
