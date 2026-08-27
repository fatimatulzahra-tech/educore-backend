from pydantic import BaseModel
from typing import Optional


class SubjectCreate(BaseModel):
    class_id: int
    name: str
    code: Optional[str] = None