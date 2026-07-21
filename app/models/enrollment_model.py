from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class Enrollment(Base):

    __tablename__ = "enrollments"

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

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    class_id = Column(
        Integer,
        ForeignKey("classes.id"),
        nullable=False
    )

    section_id = Column(
        Integer,
        ForeignKey("sections.id"),
        nullable=False
    )

    academic_year = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="active"
    )