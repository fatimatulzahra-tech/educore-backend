from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session
from datetime import date as date_type

from app.database.database import get_db

from app.models.payment_model import Payment
from app.models.student_fee_model import StudentFee
from app.models.enrollment_model import Enrollment
from app.models.student_model import Student

from app.schemas.payment_schema import (
    PaymentCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


def serialize_payment(payment: Payment) -> dict:
    return {
        "id": payment.id,
        "school_id": payment.school_id,
        "student_fee_id": payment.student_fee_id,
        "amount_paid": payment.amount_paid,
        "payment_method": payment.payment_method,
        "payment_date": payment.payment_date,
    }


def get_student_id_for_fee(db: Session, student_fee_id: int):
    """Derive student via StudentFee -> Enrollment -> Student, since
    Payment only stores student_fee_id, not student_id directly."""

    student_fee = db.query(StudentFee).filter(
        StudentFee.id == student_fee_id
    ).first()

    if not student_fee:
        return None

    enrollment = db.query(Enrollment).filter(
        Enrollment.id == student_fee.enrollment_id
    ).first()

    if not enrollment:
        return None

    return enrollment.student_id


# CREATE PAYMENT

@router.post("/")
def create_payment(

    data: PaymentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_finance"
        )
    )

):

    student_fee = db.query(StudentFee).filter(
        StudentFee.id == data.student_fee_id,
        StudentFee.school_id == current_user.school_id
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

        payment_method=data.payment_method,

        payment_date=data.payment_date or date_type.today()

    )

    db.add(payment)

    student_fee.status = "paid"

    db.commit()

    db.refresh(payment)

    return serialize_payment(payment)


# GET ALL PAYMENTS

@router.get("/")
def get_payments(

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_finance"
        )
    )

):

    query = db.query(Payment)

    query = apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user

    )

    total = query.count()

    skip = (page - 1) * limit

    payments = query.offset(
        skip
    ).limit(
        limit
    ).all()

    return {

        "page": page,

        "limit": limit,

        "total": total,

        "data": [serialize_payment(p) for p in payments]

    }


@router.get("/summary")
def payment_summary(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_finance"
        )
    )

):

    query = db.query(Payment)

    query = apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user

    )

    payments = query.all()

    total = sum(

        payment.amount_paid

        for payment in payments

    )

    return {

        "total_collection": total,

        "payments": len(payments)

    }


# STUDENT PAYMENT HISTORY

@router.get("/student/{student_id}")
def student_payments(

    student_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_finance"
        )
    )

):

    query = db.query(Payment)

    query = apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user

    )

    all_payments = query.all()

    matching = []

    for payment in all_payments:

        resolved_student_id = get_student_id_for_fee(
            db, payment.student_fee_id
        )

        if resolved_student_id == student_id:
            matching.append(serialize_payment(payment))

    return matching


# COLLECTION SUMMARY

@router.get("/collection")
def collection(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_finance"
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

    total = sum(

        payment.amount_paid

        for payment in payments

    )

    return {

        "total_collection": total,

        "total_transactions":

        len(payments)

    }


# GET SINGLE PAYMENT

@router.get("/{payment_id}")
def get_payment(

    payment_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_finance"
        )
    )

):

    query = db.query(Payment)

    query = apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user

    )

    payment = query.filter(

        Payment.id == payment_id

    ).first()

    if not payment:

        raise HTTPException(

            status_code=404,

            detail="Payment not found"

        )

    return serialize_payment(payment)