from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class Section(Base):

    __tablename__ = "sections"

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

    class_id = Column(
        Integer,
        ForeignKey("classes.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )