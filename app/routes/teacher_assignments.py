from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.class_model import Class
from app.models.section_model import Section
from app.models.student_model import Student
from app.models.teacher_assignment_model import (
    TeacherAssignment
)

from app.models.teacher_model import Teacher

from app.dependencies.permission_dependencies import (
    require_permission
)

router = APIRouter(
    prefix="/teacher-assignments",
    tags=["Teacher Assignments"]
)

# ASSIGN TEACHER

@router.post("/")
def assign_teacher(
    teacher_id: int,
    class_id: int,
    section_id: int,
    subject: str,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )
):

    assignment = TeacherAssignment(
        school_id=current_user.school_id,

        teacher_id=teacher_id,

        class_id=class_id,

        section_id=section_id,

        subject=subject
    )

    db.add(assignment)

    db.commit()

    db.refresh(assignment)

    return {
        "message":
        "Teacher assigned successfully",

        "assignment":
        assignment
    }


# GET ALL ASSIGNMENTS

@router.get("/")
def get_assignments(
    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )
):

    assignments = db.query(
        TeacherAssignment
    ).filter(

        TeacherAssignment.school_id ==
        current_user.school_id

    ).all()

    return assignments


# GET MY CLASSES (TEACHER)

# GET MY CLASSES (TEACHER)

@router.get("/my-classes")
def my_classes(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

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
        return []

    assignments = db.query(
        TeacherAssignment
    ).filter(

        TeacherAssignment.school_id ==
        current_user.school_id,

        TeacherAssignment.teacher_id ==
        teacher.id

    ).all()

    result = []

    for assignment in assignments:

        class_obj = db.query(Class).filter(
            Class.id == assignment.class_id
        ).first()

        section_obj = db.query(Section).filter(
            Section.id == assignment.section_id
        ).first()

        student_count = db.query(Student).filter(

            Student.school_id == current_user.school_id,

            Student.class_id == assignment.class_id,

            Student.section_id == assignment.section_id

        ).count()

        result.append({

            "id": assignment.id,

            "teacher_id": assignment.teacher_id,

            "subject": assignment.subject,

            "class_id": assignment.class_id,

            "class_name": class_obj.name if class_obj else "",

            "section_id": assignment.section_id,

            "section_name": section_obj.name if section_obj else "",

            "student_count": student_count

        })

    return result

@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: int,
    teacher_id: int,
    class_id: int,
    section_id: int,
    subject: str,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )
):

    assignment = db.query(
        TeacherAssignment
    ).filter(

        TeacherAssignment.id == assignment_id,

        TeacherAssignment.school_id ==
        current_user.school_id

    ).first()

    if not assignment:

        return {
            "message":
            "Assignment not found"
        }

    assignment.teacher_id = teacher_id
    assignment.class_id = class_id
    assignment.section_id = section_id
    assignment.subject = subject

    db.commit()
    db.refresh(assignment)

    return {
        "message":
        "Assignment updated successfully",

        "assignment":
        assignment
    }