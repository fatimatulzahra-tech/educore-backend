from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import uuid4

from app.database.database import get_db
from app.utils.jwt import get_current_user
from app.utils.hash import hash_password

from app.models.user_model import User
from app.models.school_model import School
from app.models.invitation_model import Invitation
from app.models.role_model import Role
from app.models.user_role_model import UserRole

from app.schemas.school_schema import SchoolCreate
from app.schemas.invitation_schema import (
    InvitePrincipalRequest,
    AcceptInvitationRequest
)

router = APIRouter(
    prefix="/platform",
    tags=["Platform"]
)


# -------------------------
# CREATE SCHOOL
# -------------------------

@router.post("/schools")
def create_school(
    data: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "platform_admin":
        return {
            "message": "Unauthorized"
        }

    existing_school = db.query(School).filter(
        School.email == data.email
    ).first()

    if existing_school:
        return {
            "message": "School email already exists"
        }

    school = School(
        name=data.name,
        slug=data.name.lower().replace(" ", "-"),
        email=data.email,
        phone=data.phone,
        address=data.address
    )

    db.add(school)

    db.commit()

    db.refresh(school)

    # SEED SCHOOL RBAC
    from app.seeds.rbac_seed import seed_rbac

    seed_rbac(
        db=db,
        school_id=school.id
    )

    return {
        "message": "School created successfully",
        "school_id": school.id
    }


# -------------------------
# GET SCHOOLS
# -------------------------

@router.get("/schools")
def get_schools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "platform_admin":
        return {
            "message": "Unauthorized"
        }

    return db.query(School).filter(
    School.is_active.is_(True)
).all()


# -------------------------
# INVITE PRINCIPAL
# -------------------------

@router.post("/invite-principal")
def invite_principal(
    data: InvitePrincipalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "platform_admin":
        return {
            "message": "Unauthorized"
        }

    school = db.query(School).filter(
        School.id == data.school_id
    ).first()

    if not school:
        return {
            "message": "School not found"
        }

    invitation_token = str(uuid4())

    invitation = Invitation(
        school_id=data.school_id,
        email=data.email,
        role="principal",
        token=invitation_token
    )

    db.add(invitation)

    db.commit()

    return {
        "message": "Principal invited successfully",
        "invitation_token": invitation_token
    }


# -------------------------
# ACCEPT INVITATION
# -------------------------

@router.post("/accept-invitation")
def accept_invitation(
    data: AcceptInvitationRequest,
    db: Session = Depends(get_db)
):

    invitation = db.query(Invitation).filter(
        Invitation.token == data.token
    ).first()

    if not invitation:
        return {
            "message": "Invalid invitation"
        }

    if invitation.is_used:
        return {
            "message": "Invitation already used"
        }

    # DEBUG ROLE VALUES

    print("ROLE IN DB:")

    for r in db.query(Role).all():
        print(repr(r.name))

    print("INVITATION ROLE:")
    print(repr(invitation.role))

    print("NORMALIZED ROLE:")
    print(repr(invitation.role.strip().lower()))

    existing_user = db.query(User).filter(
        User.email == invitation.email
    ).first()

    if existing_user:
        return {
            "message": "User already exists"
        }

    normalized_role = invitation.role.strip().lower()

    role_exists = db.query(Role).filter(
        Role.school_id == invitation.school_id,
        func.lower(Role.name) == normalized_role
    ).first()

    if not role_exists:
        return {
            "message": "Role does not exist"
        }

    try:

        # CREATE USER
        user = User(
            email=invitation.email,
            hashed_password=hash_password(data.password),
            role="principal",
            school_id=invitation.school_id,
            is_verified=True
        )

        db.add(user)

        # IMPORTANT
        db.flush()

        # ASSIGN ROLE
        user_role = UserRole(
            user_id=user.id,
            role_id=role_exists.id
        )

        db.add(user_role)

        # ASSIGN PRINCIPAL TO SCHOOL
        school = db.query(School).filter(
            School.id == invitation.school_id
        ).first()

        school.principal_id = user.id

        # MARK INVITATION USED
        invitation.is_used = True

        db.commit()

        db.refresh(user)

        return {
            "message": "Principal account created successfully",
            "user_id": user.id,
            "school_id": school.id
        }

    except Exception as e:

        db.rollback()

        return {
            "message": str(e)
        }