from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date as date_type

from app.database.database import get_db

from app.models.employee_attendance_model import EmployeeAttendance
from app.models.teacher_model import Teacher
from app.models.staff_model import Staff

from app.schemas.employee_attendance_schema import (
    EmployeeAttendanceCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

router = APIRouter(
    prefix="/employee-attendance",
    tags=["Employee Attendance"]
)


def serialize_record(record: EmployeeAttendance) -> dict:
    return {
        "id": record.id,
        "person_type": record.person_type,
        "person_id": record.person_id,
        "date": record.date,
        "status": record.status,
        "remarks": record.remarks,
    }


def upsert_attendance(
    db: Session,
    school_id: int,
    person_type: str,
    person_id: int,
    date: date_type,
    status: str
):
    existing = db.query(EmployeeAttendance).filter(
        EmployeeAttendance.school_id == school_id,
        EmployeeAttendance.person_type == person_type,
        EmployeeAttendance.person_id == person_id,
        EmployeeAttendance.date == date
    ).first()

    if existing:
        existing.status = status
        return existing

    record = EmployeeAttendance(
        school_id=school_id,
        person_type=person_type,
        person_id=person_id,
        date=date,
        status=status
    )
    db.add(record)
    return record


# -------------------------
# MARK ATTENDANCE (TEACHERS + STAFF, ONE CALL)
# -------------------------
@router.post("/")
def mark_employee_attendance(
    data: EmployeeAttendanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_teachers")
    )
):

    saved = []

    for item in data.teacher_attendance:
        record = upsert_attendance(
            db=db,
            school_id=current_user.school_id,
            person_type="teacher",
            person_id=item.teacher_id,
            date=data.date,
            status=item.status
        )
        saved.append(record)

    for item in data.staff_attendance:
        record = upsert_attendance(
            db=db,
            school_id=current_user.school_id,
            person_type="staff",
            person_id=item.staff_id,
            date=data.date,
            status=item.status
        )
        saved.append(record)

    db.commit()

    for record in saved:
        db.refresh(record)

    return {
        "message": "Employee attendance saved successfully",
        "count": len(saved)
    }


# -------------------------
# GET ATTENDANCE FOR A DATE (WITH NAMES)
# -------------------------
@router.get("/")
def get_employee_attendance(
    date: date_type,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_attendance")
    )
):

    records = db.query(EmployeeAttendance).filter(
        EmployeeAttendance.school_id == current_user.school_id,
        EmployeeAttendance.date == date
    ).all()

    teacher_map = {
        t.id: f"{t.first_name} {t.last_name}"
        for t in db.query(Teacher).filter(
            Teacher.school_id == current_user.school_id
        ).all()
    }

    staff_map = {
        s.id: f"{s.first_name} {s.last_name}"
        for s in db.query(Staff).filter(
            Staff.school_id == current_user.school_id
        ).all()
    }

    result = []

    for record in records:

        name = None

        if record.person_type == "teacher":
            name = teacher_map.get(record.person_id, "Unknown Teacher")
        elif record.person_type == "staff":
            name = staff_map.get(record.person_id, "Unknown Staff")

        result.append({
            "id": record.id,
            "person_type": record.person_type,
            "person_id": record.person_id,
            "name": name,
            "date": record.date,
            "status": record.status,
        })

    return result


# -------------------------
# DAILY SUMMARY (COUNTS)
# -------------------------
@router.get("/summary")
def employee_attendance_summary(
    date: date_type,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_attendance")
    )
):

    records = db.query(EmployeeAttendance).filter(
        EmployeeAttendance.school_id == current_user.school_id,
        EmployeeAttendance.date == date
    ).all()

    summary = {}

    for record in records:
        summary[record.status] = summary.get(record.status, 0) + 1

    return {
        "date": date,
        "total_marked": len(records),
        "by_status": summary
    }