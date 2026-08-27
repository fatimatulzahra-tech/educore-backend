from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class StaffCreate(BaseModel):

    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

    designation: Optional[str] = None
    department: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[int] = None
    salary: Optional[float] = None
    joining_date: Optional[date] = None
    employment_type: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "Active"