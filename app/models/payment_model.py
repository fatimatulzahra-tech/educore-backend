from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey
)

from app.database.database import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.id"),
        nullable=False
    )

    student_fee_id = Column(
        Integer,
        ForeignKey("student_fees.id"),
        nullable=False
    )

    amount_paid = Column(
        Float,
        nullable=False
    )

    payment_method = Column(
        String,
        nullable=False
    )