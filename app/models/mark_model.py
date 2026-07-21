from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey
)

from app.database.database import Base


class Mark(Base):

    __tablename__ = "marks"


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


    exam_id = Column(
        Integer,
        ForeignKey("exams.id"),
        nullable=False
    )


    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )


    obtained_marks = Column(
        Float,
        nullable=False
    )


    total_marks = Column(
        Float,
        nullable=False
    )