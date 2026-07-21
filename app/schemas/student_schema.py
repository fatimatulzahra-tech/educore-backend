from pydantic import BaseModel


class StudentCreate(BaseModel):

    class_id: int

    section_id: int

    first_name: str

    last_name: str
    
    email: str
    
    admission_number: str

    gender: str

    phone: str | None = None

    address: str | None = None