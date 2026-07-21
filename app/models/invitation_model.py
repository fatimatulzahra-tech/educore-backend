from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean
)

from app.database.database import Base


class Invitation(Base):

    __tablename__ = "invitations"

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

    email = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    token = Column(
        String,
        unique=True,
        nullable=False
    )

    is_used = Column(
        Boolean,
        default=False
    )