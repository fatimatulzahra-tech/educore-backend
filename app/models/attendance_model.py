from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    UniqueConstraint
)

from app.database.database import Base


class Attendance(Base):

    __tablename__ = "attendance"

    __table_args__ = (
        UniqueConstraint(
            "enrollment_id",
            "date",
            name="uq_attendance"
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

    enrollment_id = Column(
        Integer,
        ForeignKey("enrollments.id"),
        nullable=False
    )

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=True
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