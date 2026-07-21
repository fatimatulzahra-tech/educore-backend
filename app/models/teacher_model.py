from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base
from sqlalchemy import Integer, ForeignKey

class Teacher(Base):

    __tablename__ = "teachers"

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

    subject = Column(
        String,
        nullable=False
    )

    user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=True  # keep nullable for backward compatibility
    )