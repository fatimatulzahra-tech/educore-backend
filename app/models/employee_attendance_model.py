from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    UniqueConstraint
)

from app.database.database import Base


class EmployeeAttendance(Base):

    __tablename__ = "employee_attendance"

    __table_args__ = (
        UniqueConstraint(
            "person_type",
            "person_id",
            "date",
            name="uq_employee_attendance"
        ),
    )

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

    # "teacher" or "staff" — which table person_id points to
    person_type = Column(
        String,
        nullable=False
    )

    # References teachers.id when person_type == "teacher",
    # or staff.id when person_type == "staff"
    person_id = Column(
        Integer,
        nullable=False
    )

    date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    remarks = Column(
        String,
        nullable=True
    )