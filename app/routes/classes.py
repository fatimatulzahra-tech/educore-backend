from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.class_model import Class

from app.schemas.class_schema import (
    ClassCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)


# CREATE CLASS
@router.post("/")
def create_class(

    data: ClassCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    # ROLE-AWARE TENANT FILTER
    class_query = db.query(Class)

    class_query = apply_tenant_filter(
        query=class_query,
        model=Class,
        current_user=current_user
    )

    existing_class = class_query.filter(
        Class.name == data.name
    ).first()

    if existing_class:

        raise HTTPException(
            status_code=400,
            detail="Class already exists"
        )

    new_class = Class(

        school_id=current_user.school_id,

        name=data.name
    )

    db.add(new_class)

    db.commit()

    db.refresh(new_class)

    return new_class


# GET ALL CLASSES
@router.get("/")
def get_classes(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(Class)

    query = apply_tenant_filter(
        query=query,
        model=Class,
        current_user=current_user
    )

    classes = query.all()

    return classes