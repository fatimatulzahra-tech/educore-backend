from pydantic import BaseModel
from typing import Optional
from datetime import date


class TransactionCreate(BaseModel):
    type: str  # "income" | "expense" | "salary"
    category: Optional[str] = None
    amount: float
    description: Optional[str] = None
    date: date
    related_person_type: Optional[str] = None  # "teacher" | "staff"
    related_person_id: Optional[int] = None