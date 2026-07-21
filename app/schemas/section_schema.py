from pydantic import BaseModel


class SectionCreate(BaseModel):

    class_id: int
    name: str