from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class TeacherAssignment(Base):

    __tablename__ = "teacher_assignments"

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

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
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

    subject = Column(
        String,
        nullable=False
    )