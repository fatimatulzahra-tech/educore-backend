from pydantic import BaseModel


class SubjectCreate(BaseModel):

    name: str
    code: str


class ExamCreate(BaseModel):

    title: str
    class_id: int
    section_id: int
    subject_id: int
    total_marks: int


class MarkCreate(BaseModel):

    enrollment_id: int
    exam_id: int
    subject_id: int

    obtained_marks: float
    total_marks: float