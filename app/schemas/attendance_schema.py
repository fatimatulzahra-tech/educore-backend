from pydantic import BaseModel
from datetime import date


class AttendanceCreate(BaseModel):

    enrollment_id: int

    date: date

    status: str

    remarks: str | None = None