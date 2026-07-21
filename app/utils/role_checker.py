from fastapi import HTTPException

def require_role(required_role):

    def role_dependency(current_user):

        if current_user.role != required_role:

            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return role_dependency