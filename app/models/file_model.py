from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class File(Base):

    __tablename__ = "files"

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

    file_name = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )