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


def serialize_result(result: Result) -> dict:
    return {
        "id": result.id,
        "school_id": result.school_id,
        "exam_id": result.exam_id,
        "student_id": result.student_id,
        "marks": result.marks,
    }


@router.post("/")
def create_result(

    exam_id: int,

    student_id: int,

    marks: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_exams"
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

    return serialize_result(result)


@router.get("/")
def get_results(

    exam_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_exams"
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

    results = query.all()

    return [serialize_result(r) for r in results]