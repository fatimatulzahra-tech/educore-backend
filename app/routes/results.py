from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.result_model import Result

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/results",
    tags=["Results"]
)


@router.post("/")
def create_result(

    exam_id: int,

    student_id: int,

    marks: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    result = Result(

        school_id=current_user.school_id,

        exam_id=exam_id,

        student_id=student_id,

        marks=marks

    )

    db.add(result)

    db.commit()

    db.refresh(result)

    return result


@router.get("/")
def get_results(

    exam_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(Result)

    query = apply_tenant_filter(

        query=query,

        model=Result,

        current_user=current_user

    )

    query = query.filter(
        Result.exam_id == exam_id
    )

    return query.all()