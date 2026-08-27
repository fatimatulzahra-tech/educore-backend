from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as date_type

from app.database.database import get_db

from app.models.transaction_model import Transaction

from app.schemas.transaction_schema import TransactionCreate

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

VALID_TYPES = {"income", "expense", "salary"}


def serialize_transaction(t: Transaction) -> dict:
    return {
        "id": t.id,
        "school_id": t.school_id,
        "type": t.type,
        "category": t.category,
        "amount": t.amount,
        "description": t.description,
        "date": t.date,
        "related_person_type": t.related_person_type,
        "related_person_id": t.related_person_id,
    }


# -------------------------
# CREATE TRANSACTION
# -------------------------
@router.post("/")
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_finance")
    )
):

    if data.type not in VALID_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"type must be one of {sorted(VALID_TYPES)}"
        )

    if data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero"
        )

    transaction = Transaction(
        school_id=current_user.school_id,
        type=data.type,
        category=data.category,
        amount=data.amount,
        description=data.description,
        date=data.date,
        related_person_type=data.related_person_type,
        related_person_id=data.related_person_id,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return serialize_transaction(transaction)


# -------------------------
# GET TRANSACTIONS (WITH FILTERS)
# -------------------------
@router.get("/")
def get_transactions(
    type: str | None = None,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_finance")
    )
):

    query = db.query(Transaction)

    query = apply_tenant_filter(
        query=query,
        model=Transaction,
        current_user=current_user
    )

    if type:
        query = query.filter(Transaction.type == type)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.order_by(Transaction.date.desc()).all()

    return [serialize_transaction(t) for t in transactions]


# -------------------------
# SUMMARY (DAILY RECOVERY / INCOME VS EXPENSE)
# -------------------------
@router.get("/summary")
def transaction_summary(
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("view_finance")
    )
):

    query = db.query(Transaction)

    query = apply_tenant_filter(
        query=query,
        model=Transaction,
        current_user=current_user
    )

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")
    salary = sum(t.amount for t in transactions if t.type == "salary")

    return {
        "total_income": income,
        "total_expense": expense,
        "total_salary": salary,
        "net": income - expense - salary,
        "transaction_count": len(transactions),
    }


# -------------------------
# UPDATE TRANSACTION
# -------------------------
@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: int,
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_finance")
    )
):

    query = db.query(Transaction)
    query = apply_tenant_filter(
        query=query,
        model=Transaction,
        current_user=current_user
    )

    transaction = query.filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    if data.type not in VALID_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"type must be one of {sorted(VALID_TYPES)}"
        )

    transaction.type = data.type
    transaction.category = data.category
    transaction.amount = data.amount
    transaction.description = data.description
    transaction.date = data.date
    transaction.related_person_type = data.related_person_type
    transaction.related_person_id = data.related_person_id

    db.commit()
    db.refresh(transaction)

    return serialize_transaction(transaction)


# -------------------------
# DELETE TRANSACTION
# -------------------------
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("manage_finance")
    )
):

    query = db.query(Transaction)
    query = apply_tenant_filter(
        query=query,
        model=Transaction,
        current_user=current_user
    )

    transaction = query.filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}