from pydantic import BaseModel
from typing import Optional
from datetime import date


class PaymentCreate(BaseModel):
    student_fee_id: int
    amount_paid: float
    payment_method: str
    payment_date: Optional[date] = None