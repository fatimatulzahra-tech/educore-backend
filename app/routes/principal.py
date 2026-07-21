from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.utils.jwt import get_current_user

from app.models.user_model import User

router = APIRouter(
    prefix="/principal",
    tags=["Principal"]
)


@router.get("/dashboard")
def principal_dashboard(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    # ROLE SECURITY

    if current_user.role != "principal":

        return {
            "message":
            "Unauthorized"
        }

    # FUTURE REAL COUNTS
    # currently placeholders

    students_count = 0
    teachers_count = 0
    attendance_percentage = 0

    return {

        "students":
        students_count,

        "teachers":
        teachers_count,

        "attendance":
        attendance_percentage
    }