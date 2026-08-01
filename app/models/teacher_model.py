from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base
from sqlalchemy import Integer, ForeignKey
from sqlalchemy import Date, Float

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
    qualification = Column(
    String,
    nullable=True
    )

    experience = Column(
    Integer,
    nullable=True
    )

    salary = Column(
    Float,
    nullable=True
    )

    joining_date = Column(
    Date,
    nullable=True
    )

    employment_type = Column(
    String,
    nullable=True
    )