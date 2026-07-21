from fastapi import Depends, HTTPException
from app.utils.jwt import get_current_user


def get_current_school(current_user=Depends(get_current_user)):

    if not current_user.school_id:

        raise HTTPException(
            status_code=400,
            detail="User has no school assigned"
        )

    return current_user.school_id