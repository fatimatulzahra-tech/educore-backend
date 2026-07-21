from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class School(Base):

    __tablename__ = "schools"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    slug = Column(
        String,
        unique=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    phone = Column(
        String,
        nullable=True
    )

    address = Column(
        String,
        nullable=True
    )

    logo_url = Column(
        String,
        nullable=True
    )

    subscription_plan = Column(
        String,
        default="basic"
    )

    is_active = Column(
        Boolean,
        default=True
    )

    principal_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    principal = relationship(
        "User",
        foreign_keys=[principal_id]
    )

    