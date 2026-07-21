from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database.database import get_db

from app.models.student_model import Student
from app.models.class_model import Class
from app.models.section_model import Section
from app.models.attendance_model import Attendance
from app.models.payment_model import Payment
from app.models.exam_model import Exam

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# -------------------------
# PRINCIPAL DASHBOARD SUMMARY
# -------------------------
@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_students")
    )
):

    # STUDENTS
    student_query = apply_tenant_filter(
        db.query(Student),
        Student,
        current_user
    )

    total_students = student_query.count()

    # CLASSES
    class_query = apply_tenant_filter(
        db.query(Class),
        Class,
        current_user
    )

    total_classes = class_query.count()

    # SECTIONS
    section_query = apply_tenant_filter(
        query=db.query(Section),
        model=Section,
        current_user=current_user
    )

    total_sections = section_query.count()

    # ATTENDANCE
    attendance_query = apply_tenant_filter(
        db.query(Attendance),
        Attendance,
        current_user
    )

    today = date.today()

    present_today = attendance_query.filter(
        Attendance.date == "12-12-2024",
        Attendance.status == "present"
    ).count()

    absent_today = attendance_query.filter(
        Attendance.date == "12-12-2024",
        Attendance.status == "absent"
    ).count()

    late_today = attendance_query.filter(
        Attendance.date == "12-12-2024",
        Attendance.status == "late"
    ).count()

    total_today = (
        present_today +
        absent_today +
        late_today
    )

    attendance_percentage = 0

    if total_today > 0:

        attendance_percentage = round(
            (present_today / total_today) * 100,
            2
        )

    return {

        "total_students": total_students,

        "total_classes": total_classes,

        "total_sections": total_sections,

        "present_today": present_today,

        "absent_today": absent_today,

        "late_today": late_today,

        "attendance_percentage":
            attendance_percentage
    }


# -------------------------
# ANALYTICS (TENANT SAFE)
# -------------------------
@router.get("/analytics")
def dashboard_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_students")
    )
):

    student_query = apply_tenant_filter(
        db.query(Student),
        Student,
        current_user
    )

    total_students = student_query.count()

    payment_query = apply_tenant_filter(
        db.query(Payment),
        Payment,
        current_user
    )

    total_fee_collection = sum(
        p.amount_paid
        for p in payment_query.all()
    )

    attendance_query = apply_tenant_filter(
        db.query(Attendance),
        Attendance,
        current_user
    )

    present_count = attendance_query.filter(
        Attendance.status == "present"
    ).count()

    absent_count = attendance_query.filter(
        Attendance.status == "absent"
    ).count()

    late_count = attendance_query.filter(
        Attendance.status == "late"
    ).count()

    exam_query = apply_tenant_filter(
        db.query(Exam),
        Exam,
        current_user
    )

    total_exams = exam_query.count()

    return {

        "total_students":
            total_students,

        "total_fee_collection":
            total_fee_collection,

        "present_count":
            present_count,

        "absent_count":
            absent_count,

        "late_count":
            late_count,

        "total_exams":
            total_exams
    }

