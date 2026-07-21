from pydantic import BaseModel
from datetime import date


class PaymentCreate(BaseModel):

    student_id: int

    amount_paid: float

    payment_method: str

    payment_date: date