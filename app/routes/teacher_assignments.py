from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.teacher_assignment_model import TeacherAssignment
from app.models.teacher_model import Teacher
from app.models.class_model import Class
from app.models.section_model import Section
from app.models.student_model import Student
from app.models.subject_model import Subject

from app.schemas.teacher_assignment_schema import (
    TeacherAssignmentCreate,
)

from app.dependencies.permission_dependencies import (
    require_permission,
)

router = APIRouter(
    prefix="/teacher-assignments",
    tags=["Teacher Assignments"],
)


# ---------------------------------------------------
# CREATE ASSIGNMENTS
# ---------------------------------------------------

@router.post("/")
def assign_teacher(
    data: TeacherAssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_students")
    ),
):

    created = []

    for item in data.assignments:

        assignment = TeacherAssignment(
            school_id=current_user.school_id,
            teacher_id=data.teacher_id,
            class_id=item.class_id,
            section_id=item.section_id,
            subject_id=item.subject_id,
        )

        db.add(assignment)
        created.append(assignment)

    db.commit()

    return {
        "message": "Teacher assignments created successfully",
        "count": len(created),
    }


# ---------------------------------------------------
# GET ALL
# ---------------------------------------------------

@router.get("/")
def get_assignments(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_students")
    ),
):

    assignments = (
        db.query(TeacherAssignment)
        .filter(
            TeacherAssignment.school_id == current_user.school_id
        )
        .all()
    )

    return [
        {
            "id": a.id,
            "teacher_id": a.teacher_id,
            "class_id": a.class_id,
            "section_id": a.section_id,
            "subject_id": a.subject_id,
        }
        for a in assignments
    ]


# ---------------------------------------------------
# UPDATE
# ---------------------------------------------------

@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: int,
    data: TeacherAssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_students")
    ),
):

    assignment = (
        db.query(TeacherAssignment)
        .filter(
            TeacherAssignment.id == assignment_id,
            TeacherAssignment.school_id == current_user.school_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    if len(data.assignments) == 0:
        raise HTTPException(
            status_code=400,
            detail="No assignment supplied",
        )

    item = data.assignments[0]

    assignment.teacher_id = data.teacher_id
    assignment.class_id = item.class_id
    assignment.section_id = item.section_id
    assignment.subject_id = item.subject_id

    db.commit()
    db.refresh(assignment)

    return {
        "message": "Assignment updated successfully",
        "assignment": assignment,
    }


# ---------------------------------------------------
# DELETE
# ---------------------------------------------------

@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_students")
    ),
):

    assignment = (
        db.query(TeacherAssignment)
        .filter(
            TeacherAssignment.id == assignment_id,
            TeacherAssignment.school_id == current_user.school_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Assignment deleted successfully"
    }


# ---------------------------------------------------
# MY CLASSES
# ---------------------------------------------------

@router.get("/my-classes")
def my_classes(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_students")
    ),
):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.school_id == current_user.school_id,
            Teacher.email == current_user.email,
        )
        .first()
    )

    if not teacher:
        return []

    assignments = (
        db.query(TeacherAssignment)
        .filter(
            TeacherAssignment.school_id == current_user.school_id,
            TeacherAssignment.teacher_id == teacher.id,
        )
        .all()
    )

    result = []

    for assignment in assignments:

        cls = (
            db.query(Class)
            .filter(Class.id == assignment.class_id)
            .first()
        )

        section = (
            db.query(Section)
            .filter(Section.id == assignment.section_id)
            .first()
        )

        subject = (
            db.query(Subject)
            .filter(Subject.id == assignment.subject_id)
            .first()
        )

        students = (
            db.query(Student)
            .filter(
                Student.school_id == current_user.school_id,
                Student.class_id == assignment.class_id,
                Student.section_id == assignment.section_id,
            )
            .count()
        )

        result.append(
            {
                "id": assignment.id,
                "teacher_id": assignment.teacher_id,
                "subject_id": assignment.subject_id,
                "subject_name": subject.name if subject else "",
                "class_id": assignment.class_id,
                "class_name": cls.name if cls else "",
                "section_id": assignment.section_id,
                "section_name": section.name if section else "",
                "student_count": students,
            }
        )

    return result