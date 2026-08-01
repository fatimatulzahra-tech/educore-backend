from pydantic import BaseModel


class SubjectCreate(BaseModel):
    class_id: int
    name: str