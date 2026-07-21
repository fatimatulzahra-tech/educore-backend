from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class Subject(Base):

    __tablename__ = "subjects"

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

    name = Column(
        String,
        nullable=False
    )

    code = Column(
        String,
        nullable=False
    )