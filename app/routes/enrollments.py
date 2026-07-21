from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.enrollment_model import (
    Enrollment
)

from app.models.student_model import Student
from app.models.class_model import Class
from app.models.section_model import Section

from app.schemas.enrollment_schema import (
    EnrollmentCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


# CREATE ENROLLMENT
@router.post("/")
def create_enrollment(

    data: EnrollmentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    # STUDENT TENANCY FILTER
    student_query = db.query(
        Student
    )

    student_query = apply_tenant_filter(

        query=student_query,

        model=Student,

        current_user=current_user
    )

    student = student_query.filter(

        Student.id == data.student_id

    ).first()

    if not student:

        raise HTTPException(

            status_code=404,

            detail="Student not found"
        )


    # CLASS TENANCY FILTER
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


    # SECTION TENANCY FILTER
    section_query = db.query(
        Section
    )

    section_query = apply_tenant_filter(

        query=section_query,

        model=Section,

        current_user=current_user
    )

    section = section_query.filter(

        Section.id == data.section_id

    ).first()

    if not section:

        raise HTTPException(

            status_code=404,

            detail="Section not found"
        )


    existing_enrollment = db.query(
        Enrollment
    ).filter(

        Enrollment.student_id == data.student_id,

        Enrollment.academic_year
        == data.academic_year

    ).first()

    if existing_enrollment:

        raise HTTPException(

            status_code=400,

            detail=(
                "Student already enrolled "
                "for this academic year"
            )
        )

    enrollment = Enrollment(

        school_id=current_user.school_id,

        student_id=data.student_id,

        class_id=data.class_id,

        section_id=data.section_id,

        academic_year=data.academic_year
    )

    db.add(enrollment)

    db.commit()

    db.refresh(enrollment)

    return enrollment


# GET ALL ENROLLMENTS
@router.get("/")
def get_enrollments(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(
        Enrollment
    )

    query = apply_tenant_filter(

        query=query,

        model=Enrollment,

        current_user=current_user
    )

    enrollments = query.all()

    return enrollments



