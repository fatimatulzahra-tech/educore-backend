from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.teacher_model import Teacher
from app.models.teacher_assignment_model import TeacherAssignment
from app.models.enrollment_model import Enrollment


def verify_teacher_assignment(
    db: Session,
    current_user,
    enrollment
):

    teacher = db.query(
        Teacher
    ).filter(
        Teacher.school_id ==
        current_user.school_id,

        Teacher.email ==
        current_user.email
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=403,
            detail="Teacher not found"
        )

    assignment = db.query(
        TeacherAssignment
    ).filter(

        TeacherAssignment.school_id ==
        current_user.school_id,

        TeacherAssignment.teacher_id ==
        teacher.id,

        TeacherAssignment.class_id ==
        enrollment.class_id,

        TeacherAssignment.section_id ==
        enrollment.section_id

    ).first()

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized class access"
        )

    return teacher