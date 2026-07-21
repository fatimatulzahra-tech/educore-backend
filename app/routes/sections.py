from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.section_model import Section
from app.models.class_model import Class

from app.schemas.section_schema import (
    SectionCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/sections",
    tags=["Sections"]
)


# CREATE SECTION
@router.post("/")
def create_section(

    data: SectionCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    class_query = db.query(
        Class
    )

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

    existing_section = db.query(
        Section
    ).filter(

        Section.class_id == data.class_id,

        Section.name == data.name

    ).first()

    if existing_section:

        raise HTTPException(

            status_code=400,

            detail="Section already exists"
        )

    new_section = Section(

        school_id=current_user.school_id,

        class_id=data.class_id,

        name=data.name
    )

    db.add(new_section)

    db.commit()

    db.refresh(new_section)

    return new_section


# GET ALL SECTIONS
@router.get("/")
def get_sections(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(
        Section
    )

    query = apply_tenant_filter(

        query=query,

        model=Section,

        current_user=current_user
    )

    sections = query.all()

    return sections