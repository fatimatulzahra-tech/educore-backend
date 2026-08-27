from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)
from app.models.teacher_model import Teacher
from app.models.teacher_assignment_model import TeacherAssignment
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models.class_model import Class
from app.models.section_model import Section
from app.models.teacher_model import Teacher
from app.models.teacher_assignment_model import TeacherAssignment

from app.utils.attendance_permissions import (
    verify_teacher_assignment
)
from app.database.database import get_db

from app.models.student_model import Student
from app.models.enrollment_model import Enrollment
from app.models.attendance_model import Attendance

from app.schemas.attendance_schema import (
    AttendanceCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


def serialize_attendance(attendance: Attendance) -> dict:
    return {
        "id": attendance.id,
        "school_id": attendance.school_id,
        "teacher_id": attendance.teacher_id,
        "enrollment_id": attendance.enrollment_id,
        "date": attendance.date,
        "status": attendance.status,
        "remarks": attendance.remarks,
    }


# MARK ATTENDANCE
@router.post("/")
def mark_attendance(

    data: AttendanceCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("mark_attendance")
    )

):

    teacher = db.query(Teacher).filter(
        Teacher.school_id == current_user.school_id,
        Teacher.user_id == current_user.id
    ).first()

    existing = db.query(Attendance).filter(
    Attendance.school_id == current_user.school_id,
    Attendance.enrollment_id == data.enrollment_id,
    Attendance.date == data.date
    ).first()

    if existing:

        existing.status = data.status
        existing.remarks = data.remarks

        if teacher:
            existing.teacher_id = teacher.id

        db.commit()

        return {
            "message": "Attendance updated successfully"
        }

    attendance = Attendance(

        school_id=current_user.school_id,

        teacher_id=teacher.id if teacher else None,

        enrollment_id=data.enrollment_id,

        date=data.date,

        status=data.status,

        remarks=data.remarks

    )

    db.add(attendance)

    db.commit()

    db.refresh(attendance)

    return {
        "message": "Attendance saved successfully",
        "attendance": serialize_attendance(attendance)
    }




# GET ATTENDANCE
@router.get("/")
def get_attendance(

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    status: str | None = None,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )

):

    query = db.query(
        Attendance
    )

    query = apply_tenant_filter(

        query=query,

        model=Attendance,

        current_user=current_user

    )

    if status:

        query = query.filter(

            Attendance.status ==
            status

        )

    total = query.count()

    skip = (page - 1) * limit

    attendance = query.offset(
        skip
    ).limit(
        limit
    ).all()

    return {

        "page": page,

        "limit": limit,

        "total": total,

        "data": [serialize_attendance(a) for a in attendance]

    }


# CLASS STUDENTS
@router.get("/class-students")
def get_class_students(
    class_id: int,
    section_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("mark_attendance"))
):

    enrollments = db.query(Enrollment).filter(
        Enrollment.school_id == current_user.school_id,
        Enrollment.class_id == class_id,
        Enrollment.section_id == section_id,
        Enrollment.status == "active"
    ).all()

    students = []

    for enrollment in enrollments:

        student = db.query(Student).filter(
            Student.id == enrollment.student_id
        ).first()

        if student:

            students.append({
                "enrollment_id": enrollment.id,
                "student_id": student.id,
                "student_name": f"{student.first_name} {student.last_name}",
                "admission_number": student.admission_number
            })

    return {
        "students": students
    }
@router.get("/teacher-history")
def teacher_attendance_history(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("mark_attendance")
    )

):

    teacher = db.query(Teacher).filter(
        Teacher.school_id == current_user.school_id,
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        return []

    records = (
        db.query(Attendance)
        .filter(
            Attendance.school_id == current_user.school_id,
            Attendance.teacher_id == teacher.id
        )
        .order_by(Attendance.date.desc())
        .all()
    )

    result = []

    seen = set()

    for record in records:

        enrollment = db.query(Enrollment).filter(
            Enrollment.id == record.enrollment_id
        ).first()

        if not enrollment:
            continue

        key = (
            record.date,
            enrollment.class_id,
            enrollment.section_id
        )

        if key in seen:
            continue

        seen.add(key)

        class_obj = db.query(Class).filter(
            Class.id == enrollment.class_id
        ).first()

        section_obj = db.query(Section).filter(
            Section.id == enrollment.section_id
        ).first()

        result.append({

            "date": record.date,

            "class_id": enrollment.class_id,

            "section_id": enrollment.section_id,

            "class_name": class_obj.name if class_obj else "",

            "section_name": section_obj.name if section_obj else ""

        })

    return result


@router.get("/teacher-history/details")
def teacher_attendance_details(

    class_id: int,

    section_id: int,

    date: date,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("mark_attendance")
    )

):

    teacher = db.query(Teacher).filter(
        Teacher.school_id == current_user.school_id,
        Teacher.user_id == current_user.id
    ).first()

    if not teacher:
        return []

    enrollments = db.query(Enrollment).filter(
        Enrollment.school_id == current_user.school_id,
        Enrollment.class_id == class_id,
        Enrollment.section_id == section_id
    ).all()

    result = []

    for enrollment in enrollments:

        attendance = db.query(Attendance).filter(
            Attendance.enrollment_id == enrollment.id,
            Attendance.date == date
        ).first()

        student = db.query(Student).filter(
            Student.id == enrollment.student_id
        ).first()

        if not student:
            continue

        result.append({

            "student_name":
                f"{student.first_name} {student.last_name}",

            "admission_number":
                student.admission_number,

            "status":
                attendance.status if attendance else "Not Marked"

        })

    return result


@router.get("/class-summary")
def class_summary(

    class_id: int,
    section_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
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
        class_id,

        TeacherAssignment.section_id ==
        section_id

    ).first()

    if not assignment:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized class"
        )

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.school_id ==
        current_user.school_id,

        Enrollment.class_id ==
        class_id,

        Enrollment.section_id ==
        section_id

    ).all()

    enrollment_ids = [
        e.id
        for e in enrollments
    ]

    present = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        ),

        Attendance.status ==
        "present"

    ).count()

    absent = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        ),

        Attendance.status ==
        "absent"

    ).count()

    late = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        ),

        Attendance.status ==
        "late"

    ).count()

    leave = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        ),

        Attendance.status ==
        "leave"

    ).count()

    total = present + absent + late + leave

    percentage = 0

    if total:
        percentage = round(
            present * 100 / total,
            2
        )

    return {

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        percentage
    }


@router.get("/student-summary")
def student_summary(

    enrollment_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.school_id ==
        current_user.school_id,

        Attendance.enrollment_id ==
        enrollment_id

    ).all()

    present = len([
        a for a in attendance
        if a.status == "present"
    ])

    absent = len([
        a for a in attendance
        if a.status == "absent"
    ])

    late = len([
        a for a in attendance
        if a.status == "late"
    ])

    leave = len([
        a for a in attendance
        if a.status == "leave"
    ])

    total = len(attendance)

    percentage = 0

    if total:
        percentage = round(
            present * 100 / total,
            2
        )

    return {

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        percentage
    }


@router.get("/monthly-summary")
def monthly_summary(

    enrollment_id: int,

    month: int,

    year: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.school_id ==
        current_user.school_id,

        Attendance.enrollment_id ==
        enrollment_id,

        func.extract(
            "month",
            Attendance.date
        ) == month,

        func.extract(
            "year",
            Attendance.date
        ) == year

    ).all()

    present = len([
        a for a in attendance
        if a.status == "present"
    ])

    absent = len([
        a for a in attendance
        if a.status == "absent"
    ])

    late = len([
        a for a in attendance
        if a.status == "late"
    ])

    leave = len([
        a for a in attendance
        if a.status == "leave"
    ])

    total = len(attendance)

    percentage = 0

    if total:
        percentage = round(
            present * 100 / total,
            2
        )

    return {

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        percentage
    }


@router.get("/low-attendance")
def low_attendance(

    class_id: int,

    section_id: int,

    threshold: int = 75,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.school_id ==
        current_user.school_id,

        Enrollment.class_id ==
        class_id,

        Enrollment.section_id ==
        section_id

    ).all()

    result = []

    for enrollment in enrollments:

        attendance = db.query(
            Attendance
        ).filter(

            Attendance.enrollment_id ==
            enrollment.id

        ).all()

        total = len(attendance)

        present = len([
            a for a in attendance
            if a.status == "present"
        ])

        percentage = 0

        if total:
            percentage = (
                present * 100
            ) / total

        if percentage < threshold:

            student = db.query(
                Student
            ).filter(

                Student.id ==
                enrollment.student_id

            ).first()

            if student:

                result.append({

                    "student_id":
                    student.id,

                    "student_name":
                    f"{student.first_name} "
                    f"{student.last_name}",

                    "attendance_percentage":
                    round(
                        percentage,
                        2
                    )
                })

    return result


@router.get("/today-summary")
def today_summary(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    from datetime import date

    today = date.today()

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.school_id ==
        current_user.school_id,

        Attendance.date ==
        today

    ).all()

    present = len([
        a for a in attendance
        if a.status == "present"
    ])

    absent = len([
        a for a in attendance
        if a.status == "absent"
    ])

    late = len([
        a for a in attendance
        if a.status == "late"
    ])

    leave = len([
        a for a in attendance
        if a.status == "leave"
    ])

    total = len(attendance)

    percentage = 0

    if total:
        percentage = round(
            present * 100 / total,
            2
        )

    return {

        "date": today,

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        percentage
    }


@router.get("/class-report")
def class_report(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.school_id ==
        current_user.school_id

    ).all()

    reports = []

    grouped = {}

    for e in enrollments:

        key = (
            e.class_id,
            e.section_id
        )

        grouped.setdefault(
            key,
            []
        ).append(e)

    for key, values in grouped.items():

        enrollment_ids = [
            x.id
            for x in values
        ]

        attendance = db.query(
            Attendance
        ).filter(

            Attendance.enrollment_id.in_(
                enrollment_ids
            )

        ).all()

        total = len(attendance)

        present = len([
            a for a in attendance
            if a.status == "present"
        ])

        percentage = 0

        if total:
            percentage = (
                present * 100
            ) / total

        reports.append({

            "class_id":
            key[0],

            "section_id":
            key[1],

            "attendance_percentage":
            round(
                percentage,
                2
            )
        })

    return reports

@router.get("/monthly-report")
def monthly_report(

    month: int,

    year: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.school_id ==
        current_user.school_id,

        func.extract(
            "month",
            Attendance.date
        ) == month,

        func.extract(
            "year",
            Attendance.date
        ) == year

    ).all()

    total = len(attendance)

    present = len([
        a for a in attendance
        if a.status == "present"
    ])

    absent = len([
        a for a in attendance
        if a.status == "absent"
    ])

    late = len([
        a for a in attendance
        if a.status == "late"
    ])

    leave = len([
        a for a in attendance
        if a.status == "leave"
    ])

    percentage = 0

    if total:
        percentage = (
            present * 100
        ) / total

    return {

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        round(
            percentage,
            2
        )
    }


@router.get("/yearly-report")
def yearly_report(

    year: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.school_id ==
        current_user.school_id,

        func.extract(
            "year",
            Attendance.date
        ) == year

    ).all()

    total = len(attendance)

    present = len([
        a for a in attendance
        if a.status == "present"
    ])

    absent = len([
        a for a in attendance
        if a.status == "absent"
    ])

    late = len([
        a for a in attendance
        if a.status == "late"
    ])

    leave = len([
        a for a in attendance
        if a.status == "leave"
    ])

    percentage = 0

    if total:
        percentage = (
            present * 100
        ) / total

    return {

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        round(
            percentage,
            2
        )
    }

@router.get("/low-attendance-school")
def low_attendance_school(

    threshold: int = 75,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.school_id ==
        current_user.school_id

    ).all()

    result = []

    for enrollment in enrollments:

        attendance = db.query(
            Attendance
        ).filter(

            Attendance.enrollment_id ==
            enrollment.id

        ).all()

        total = len(attendance)

        present = len([
            a for a in attendance
            if a.status == "present"
        ])

        percentage = 0

        if total:
            percentage = (
                present * 100
            ) / total

        if percentage < threshold:

            student = db.query(
                Student
            ).filter(

                Student.id ==
                enrollment.student_id

            ).first()

            if student:

                result.append({

                    "student_id":
                    student.id,

                    "student_name":
                    f"{student.first_name} "
                    f"{student.last_name}",

                    "attendance_percentage":
                    round(
                        percentage,
                        2
                    )
                })

    return result


@router.get("/my")
def my_attendance(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    student = db.query(
        Student
    ).filter(

        Student.school_id ==
        current_user.school_id,

        Student.email ==
        current_user.email

    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.school_id ==
        current_user.school_id,

        Enrollment.student_id ==
        student.id

    ).all()

    enrollment_ids = [
        e.id
        for e in enrollments
    ]

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.school_id ==
        current_user.school_id,

        Attendance.enrollment_id.in_(
            enrollment_ids
        )

    ).order_by(
        Attendance.date.desc()
    ).all()

    return [serialize_attendance(a) for a in attendance]


@router.get("/my-summary")
def my_summary(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    student = db.query(
        Student
    ).filter(

        Student.school_id ==
        current_user.school_id,

        Student.email ==
        current_user.email

    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.student_id ==
        student.id

    ).all()

    enrollment_ids = [
        e.id
        for e in enrollments
    ]

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        )

    ).all()

    present = len([
        a for a in attendance
        if a.status == "present"
    ])

    absent = len([
        a for a in attendance
        if a.status == "absent"
    ])

    late = len([
        a for a in attendance
        if a.status == "late"
    ])

    leave = len([
        a for a in attendance
        if a.status == "leave"
    ])

    total = len(attendance)

    percentage = 0

    if total:
        percentage = round(
            present * 100 / total,
            2
        )

    return {

        "present": present,

        "absent": absent,

        "late": late,

        "leave": leave,

        "attendance_percentage":
        percentage
    }


@router.get("/my-monthly")
def my_monthly(

    month: int,

    year: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    student = db.query(
        Student
    ).filter(

        Student.school_id ==
        current_user.school_id,

        Student.email ==
        current_user.email

    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.student_id ==
        student.id

    ).all()

    enrollment_ids = [
        e.id
        for e in enrollments
    ]

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        ),

        func.extract(
            "month",
            Attendance.date
        ) == month,

        func.extract(
            "year",
            Attendance.date
        ) == year

    ).all()

    return [serialize_attendance(a) for a in attendance]


@router.get("/my-yearly")
def my_yearly(

    year: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_attendance"
        )
    )
):

    student = db.query(
        Student
    ).filter(

        Student.school_id ==
        current_user.school_id,

        Student.email ==
        current_user.email

    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    enrollments = db.query(
        Enrollment
    ).filter(

        Enrollment.student_id ==
        student.id

    ).all()

    enrollment_ids = [
        e.id
        for e in enrollments
    ]

    attendance = db.query(
        Attendance
    ).filter(

        Attendance.enrollment_id.in_(
            enrollment_ids
        ),

        func.extract(
            "year",
            Attendance.date
        ) == year

    ).all()

    return [serialize_attendance(a) for a in attendance]