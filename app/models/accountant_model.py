from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base


class Accountant(Base):

    __tablename__ = "accountants"

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

    first_name = Column(
        String,
        nullable=False
    )

    last_name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )