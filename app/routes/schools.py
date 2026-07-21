from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.school_model import School
from app.schemas.school_schema import SchoolCreate, InviteUser, AcceptInvitationRequest
from app.models.invitation_model import Invitation
from app.utils.token_generator import generate_token

from app.models.role_model import Role
from app.models.user_role_model import UserRole
from app.models.user_model import User

from app.seeds.rbac_seed import seed_rbac
from app.utils.hash import hash_password
from fastapi import HTTPException
router = APIRouter(
    prefix="/schools",
    tags=["Schools"]
)

# -------------------------
# CREATE SCHOOL
# -------------------------
@router.post("/")
def create_school(
    data: SchoolCreate,
    db: Session = Depends(get_db)
):

    school = School(
        name=data.name,
        slug=data.slug,
        email=data.email,
        phone=data.phone,
        address=data.address
    )

    db.add(school)
    db.commit()
    db.refresh(school)

    # RBAC seed (tenant level roles)
    seed_rbac(db=db, school_id=school.id)

    return {
        "message": "School created",
        "school_id": school.id
    }


# -------------------------
# INVITE USER
# -------------------------
@router.post("/{school_id}/invite")
def invite_user(
    school_id: int,
    data: InviteUser,
    db: Session = Depends(get_db)
):

    token = generate_token()

    invitation = Invitation(
        school_id=school_id,
        email=data.email,
        role=data.role,
        token=token
    )

    db.add(invitation)
    db.commit()

    return {
        "message": "Invitation created",
        "invite_token": token
    }


# -------------------------
# ACCEPT INVITATION (FIXED SAAS FLOW)
# -------------------------
@router.post("/accept-invite")
def accept_invitation(
    data: AcceptInvitationRequest,
    db: Session = Depends(get_db)
):

    invitation = db.query(Invitation).filter(
        Invitation.token == data.token
    ).first()

    if not invitation:
        return {"message": "Invalid invitation token"}

    if invitation.is_used:
        return {"message": "Invitation already used"}

    # CHECK USER
    existing_user = db.query(User).filter(
        User.email == invitation.email
    ).first()

    if existing_user:
        return {"message": "User already exists"}

    # ROLE CHECK (TENANT SAFE)
    role = db.query(Role).filter(
        Role.school_id == invitation.school_id,
        Role.name == invitation.role
    ).first()

    if not role:
        return {"message": "Role does not exist"}

    try:
        # CREATE USER
        new_user = User(
            school_id=invitation.school_id,
            email=invitation.email,
            hashed_password=hash_password(data.password),
            is_verified=True,
            role=invitation.role  # IMPORTANT: fixes your "user" issue
        )

        db.add(new_user)
        db.flush()  # get user.id safely

        # ASSIGN ROLE (RBAC TABLE)
        user_role = UserRole(
            user_id=new_user.id,
            role_id=role.id
        )

        db.add(user_role)

        # -------------------------
        # FIX: LINK SCHOOL → PRINCIPAL (SAAS OWNERSHIP)
        # -------------------------
        school = db.query(School).filter(
            School.id == invitation.school_id
        ).first()

        if school and invitation.role == "principal":
            school.principal_id = new_user.id

        # MARK INVITATION USED
        invitation.is_used = True

        db.commit()

        return {
            "message": "Account created successfully",
            "user_id": new_user.id
        }

    except Exception as e:
        db.rollback()
        return {
            "message": str(e)
        }

@router.patch("/{school_id}/deactivate")
def deactivate_school(
    school_id: int,
    db: Session = Depends(get_db)
):
    school = db.query(School).filter(
        School.id == school_id
    ).first()

    if not school:
        raise HTTPException(
            status_code=404,
            detail="School not found"
        )

    school.is_active = False
    db.commit()

    return {
        "message": "School deactivated"
    }