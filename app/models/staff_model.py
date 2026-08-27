from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey
)

from app.database.database import Base


class Staff(Base):

    __tablename__ = "staff"

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

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
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

    designation = Column(
        String,
        nullable=True
    )

    department = Column(
        String,
        nullable=True
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

    address = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="Active"
    )