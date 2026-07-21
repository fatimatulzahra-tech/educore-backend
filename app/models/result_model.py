from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)

from app.database.database import Base


class Result(Base):

    __tablename__ = "results"

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

    exam_id = Column(
        Integer,
        ForeignKey("exams.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    marks = Column(
        Integer,
        nullable=False
    )