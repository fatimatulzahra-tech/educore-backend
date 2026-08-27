from pydantic import BaseModel
from typing import List


class AssignmentItem(BaseModel):
    class_id: int
    section_id: int
    subject_id: int          # was: subject: str


class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    assignments: List[AssignmentItem]