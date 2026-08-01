from datetime import date
from pydantic import BaseModel


class StudentCreate(BaseModel):

    class_id: int
    section_id: int

    first_name: str
    last_name: str

    email: str

    admission_number: str
    admission_date: date

    gender: str

    date_of_birth: date

    parent_name: str
    parent_phone: str

    phone: str | None = None
    address: str | None = None