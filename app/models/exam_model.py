from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class Exam(Base):

    __tablename__ = "exams"

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

    title = Column(
        String,
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

    subject_id = Column(
    Integer,
    ForeignKey("subjects.id"),
    nullable=False
)

    total_marks = Column(
        Integer,
        nullable=False
    )