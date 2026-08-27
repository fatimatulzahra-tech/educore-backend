from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    ForeignKey
)

from app.database.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

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

    # "income", "expense", or "salary"
    type = Column(
        String,
        nullable=False
    )

    # e.g. "Fee Collection", "Utility Bill", "Teacher Salary",
    # "Stationery", "Donation" — free-text grouping label
    category = Column(
        String,
        nullable=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    date = Column(
        Date,
        nullable=False
    )

    # Only used when type == "salary": who was paid.
    # "teacher" or "staff" — mirrors EmployeeAttendance's pattern.
    related_person_type = Column(
        String,
        nullable=True
    )

    related_person_id = Column(
        Integer,
        nullable=True
    )