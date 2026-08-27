from pydantic import BaseModel
from typing import List
from datetime import date


class TeacherAttendanceItem(BaseModel):
    teacher_id: int
    status: str


class StaffAttendanceItem(BaseModel):
    staff_id: int
    status: str


class EmployeeAttendanceCreate(BaseModel):
    date: date
    teacher_attendance: List[TeacherAttendanceItem] = []
    staff_attendance: List[StaffAttendanceItem] = []