from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey
)

from app.database.database import Base


class StudentFee(Base):

    __tablename__ = "student_fees"

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

    enrollment_id = Column(
        Integer,
        ForeignKey("enrollments.id"),
        nullable=False
    )

    fee_plan_id = Column(
        Integer,
        ForeignKey("fee_plans.id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String,
        default="unpaid"
    )