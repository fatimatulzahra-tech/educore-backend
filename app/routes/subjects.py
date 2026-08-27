from fastapi import (
    APIRouter,
    Depends,
    HTTPException
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


def serialize_subject(subject: Subject) -> dict:
    return {
        "id": subject.id,
        "school_id": subject.school_id,
        "class_id": subject.class_id,
        "name": subject.name,
        "code": subject.code,
    }


# -------------------------
# CREATE SUBJECT
# -------------------------
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
        code=data.code
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return serialize_subject(new_subject)


# -------------------------
# GET ALL SUBJECTS
# -------------------------
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
    return [serialize_subject(s) for s in subjects]


# -------------------------
# UPDATE SUBJECT
# -------------------------
@router.put("/{subject_id}")
def update_subject(
    subject_id: int,
    data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )
):
    query = db.query(Subject)
    query = apply_tenant_filter(
        query=query,
        model=Subject,
        current_user=current_user
    )
    subject = query.filter(
        Subject.id == subject_id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    subject_name = data.name.strip()

    duplicate_query = db.query(Subject)
    duplicate_query = apply_tenant_filter(
        query=duplicate_query,
        model=Subject,
        current_user=current_user
    )
    duplicate = duplicate_query.filter(
        Subject.class_id == data.class_id,
        Subject.name == subject_name,
        Subject.id != subject_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Subject already exists"
        )

    subject.class_id = data.class_id
    subject.name = subject_name
    subject.code = data.code

    db.commit()
    db.refresh(subject)

    return serialize_subject(subject)


# -------------------------
# DELETE SUBJECT
# -------------------------
@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )
):
    query = db.query(Subject)
    query = apply_tenant_filter(
        query=query,
        model=Subject,
        current_user=current_user
    )
    subject = query.filter(
        Subject.id == subject_id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    db.delete(subject)
    db.commit()

    return {
        "message": "Subject deleted successfully"
    }