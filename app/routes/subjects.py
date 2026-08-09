from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.subject_model import Subject
from app.models.class_model import Class

from app.schemas.subject_schema import (
    SubjectCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# CREATE SUBJECT

@router.post("/")
def create_subject(

    data: SubjectCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    class_query = db.query(Class)

    class_query = apply_tenant_filter(
        query=class_query,
        model=Class,
        current_user=current_user
    )

    school_class = class_query.filter(
        Class.id == data.class_id
    ).first()

    if not school_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )
    subject_name = data.name.strip()
    subject_query = db.query(Subject)

    subject_query = apply_tenant_filter(
        query=subject_query,
        model=Subject,
        current_user=current_user
    )

    existing_subject = subject_query.filter(
        Subject.class_id == data.class_id,
        Subject.name == subject_name
    ).first()

    if existing_subject:

        raise HTTPException(
            status_code=400,
            detail="Subject already exists"
        )

    new_subject = Subject(

        school_id=current_user.school_id,

        class_id=data.class_id,

        name=subject_name,

        code=None

    )

    db.add(new_subject)

    db.commit()

    db.refresh(new_subject)

    return new_subject


# GET ALL SUBJECTS

@router.get("/")
def get_subjects(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(Subject)

    query = apply_tenant_filter(
        query=query,
        model=Subject,
        current_user=current_user
    )

    subjects = query.all()

    return subjects