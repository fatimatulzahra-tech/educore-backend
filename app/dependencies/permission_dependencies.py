from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user_role_model import UserRole
from app.models.role_permission_model import RolePermission
from app.models.permission_model import Permission
from app.utils.jwt import get_current_user


def require_permission(permission_name: str):

    def checker(

        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)

    ):

        # 🔥 PLATFORM ADMIN BYPASS (CRITICAL)
        if current_user.role == "platform_admin":
            return current_user

        # STEP 1: roles
        role_ids = db.query(UserRole.role_id).filter(
            UserRole.user_id == current_user.id
        ).all()

        role_ids = [r[0] for r in role_ids]

        if not role_ids:
            raise HTTPException(
                status_code=403,
                detail="No roles assigned"
            )

        # STEP 2: permissions
        permission_ids = db.query(RolePermission.permission_id).filter(
            RolePermission.role_id.in_(role_ids)
        ).all()

        permission_ids = [p[0] for p in permission_ids]

        if not permission_ids:
            raise HTTPException(
                status_code=403,
                detail="No permissions assigned"
            )

        permission_names = db.query(Permission.name).filter(
            Permission.id.in_(permission_ids)
        ).all()

        permission_names = [p[0] for p in permission_names]

        if permission_name not in permission_names:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return checker