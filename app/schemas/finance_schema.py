from pydantic import BaseModel


class FeePlanCreate(BaseModel):

    name: str
    amount: float


class StudentFeeCreate(BaseModel):

    enrollment_id: int
    fee_plan_id: int
    amount: float


class PaymentCreate(BaseModel):

    student_fee_id: int
    amount_paid: float
    payment_method: str