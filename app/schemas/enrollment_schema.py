from pydantic import BaseModel


class EnrollmentCreate(BaseModel):

    student_id: int
    class_id: int
    section_id: int
    academic_year: str