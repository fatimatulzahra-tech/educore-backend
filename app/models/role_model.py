from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class Role(Base):

    __tablename__ = "roles"

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

    description = Column(
        String,
        nullable=True
    )