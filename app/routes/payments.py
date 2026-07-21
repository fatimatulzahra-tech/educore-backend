from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.payment_model import Payment

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


# CREATE PAYMENT

@router.post("/")
def create_payment(

    data: PaymentCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    payment = Payment(

        school_id=current_user.school_id,

        student_id=data.student_id,

        amount_paid=data.amount_paid,

        payment_method=data.payment_method,

        payment_date=data.payment_date

    )

    db.add(payment)

    db.commit()

    db.refresh(payment)

    return payment


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
            "view_students"
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

        "data": payments

    }

@router.get("/summary")
def payment_summary(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
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
            "view_students"
        )
    )

):

    query = db.query(Payment)

    query = apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user

    )

    payments = query.filter(

        Payment.student_id == student_id

    ).all()

    return payments


# COLLECTION SUMMARY

@router.get("/collection")
def collection(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query=db.query(
        Payment
    )

    query=apply_tenant_filter(

        query=query,

        model=Payment,

        current_user=current_user

    )

    payments=query.all()

    total=sum(

        payment.amount_paid

        for payment in payments

    )

    return{

        "total_collection":total,

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
            "view_students"
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

    return payment


