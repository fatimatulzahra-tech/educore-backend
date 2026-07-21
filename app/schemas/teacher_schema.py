from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

    # optional now, will be used in assignment phase
    subject: Optional[str] = None