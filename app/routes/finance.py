from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.fee_plan_model import FeePlan
from app.models.student_fee_model import (
    StudentFee
)
from app.models.payment_model import Payment

from app.models.enrollment_model import (
    Enrollment
)

from app.schemas.finance_schema import (
    FeePlanCreate,
    StudentFeeCreate,
    PaymentCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/finance",
    tags=["Finance"]
)


# CREATE FEE PLAN
@router.post("/fee-plans")
def create_fee_plan(

    data: FeePlanCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    fee_plan = FeePlan(

        school_id=current_user.school_id,

        name=data.name,

        amount=data.amount
    )

    db.add(fee_plan)

    db.commit()

    db.refresh(fee_plan)

    return fee_plan


# ASSIGN FEE TO STUDENT
@router.post("/student-fees")
def assign_fee(

    data: StudentFeeCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    enrollment_query = db.query(
        Enrollment
    )

    enrollment_query = apply_tenant_filter(

        query=enrollment_query,

        model=Enrollment,

        current_user=current_user
    )

    enrollment = enrollment_query.filter(

        Enrollment.id == data.enrollment_id

    ).first()

    if not enrollment:

        raise HTTPException(

            status_code=404,

            detail="Enrollment not found"
        )

    student_fee = StudentFee(

        school_id=current_user.school_id,

        enrollment_id=data.enrollment_id,

        fee_plan_id=data.fee_plan_id,

        amount=data.amount
    )

    db.add(student_fee)

    db.commit()

    db.refresh(student_fee)

    return student_fee


# MAKE PAYMENT
@router.post("/payments")
def make_payment(

    data: PaymentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    student_fee_query = db.query(
        StudentFee
    )

    student_fee_query = apply_tenant_filter(

        query=student_fee_query,

        model=StudentFee,

        current_user=current_user
    )

    student_fee = student_fee_query.filter(

        StudentFee.id == data.student_fee_id

    ).first()

    if not student_fee:

        raise HTTPException(

            status_code=404,

            detail="Student fee not found"
        )

    payment = Payment(

        school_id=current_user.school_id,

        student_fee_id=data.student_fee_id,

        amount_paid=data.amount_paid,

        payment_method=data.payment_method
    )

    db.add(payment)

    student_fee.status = "paid"

    db.commit()

    db.refresh(payment)

    return payment


# GET PAYMENTS
@router.get("/payments")
def get_payments(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    query = db.query(
        Payment
    )

    query = apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user
    )

    payments = query.all()

    return payments